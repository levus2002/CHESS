from Persistence.Board import Board
from Persistence.Player import Player
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import json
import os
import copy
import uuid
from collections import deque

# replay buffer instead of "online training"
class ReplayBuffer:
    def __init__(self, capacity=10000):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)

    def add(self, state, action_feats, reward, next_state, next_action_feats, done):
        self.buffer.append((state, action_feats, reward, next_state, next_action_feats, done))

    def sample(self, batch_size):
        batch = random.sample(self.buffer, min(batch_size, len(self.buffer)))
        return batch

    def __len__(self):
        return len(self.buffer)
    
class Chess4Env:
    def __init__(self):
        self.board = initgamestart()
        self.rewards=[[] for _ in range(4)]

    def reset(self):
        self.board.newgame()
        self.rewards=[[] for _ in range(4)]

    def step(self, action):
        current_player = self.board.current_player_index
        self.board.make_move(action)
        reward = self.board.get_reward(current_player)
        self.rewards[current_player-1].append(reward)
        self.board.reset_reward(current_player) 
        done = self.board.is_game_over
        if done:
            next_state = None
        else:
            next_state = self.board.encode_state()
        info = {"current_player": self.board.current_player_index, "msg": self.board.msg}
        if done:
            winner = self.board.get_winner()
            if current_player == winner:
                reward += 1
            else:
                if winner is not None:
                    reward -= 1
        return next_state, reward, done, info
    
    def statistics(self,turn_count,match_type):
        filename,p1control,p2control,p3control,p4control=get_controls(match_type)
        game_stats = {
        "turns": turn_count,
        "Is_finished": self.board.is_game_over,
        "players": {
            "1": {"Control_Type":p1control,"rewards": self.rewards[0],"Has_Lost":self.board.player1.IsDefeated},
            "2": {"Control_Type":p2control,"rewards": self.rewards[1],"Has_Lost":self.board.player2.IsDefeated},
            "3": {"Control_Type":p3control,"rewards": self.rewards[2],"Has_Lost":self.board.player3.IsDefeated},
            "4": {"Control_Type":p4control,"rewards": self.rewards[3],"Has_Lost":self.board.player4.IsDefeated}
        }
        }
        save_game_stats(filename,game_stats)
    

def get_controls(type):
    match type:
        case "4random":
            return  ("./4rand.jsonl","random","random","random","random")
        case "1agent":
            return ("./1agent.jsonl","agent","random","random","random")
        case "4agent":
            return ("./4agent.jsonl","agent","agent","agent","agent")
    return  ("./4rand.jsonl","random","random","random","random")
        
def save_game_stats(filename, stats):
    with open(filename, "a") as f:
        f.write(json.dumps(stats) + "\n")

def action_to_features( action, board):
    """
    15 features:
    0..3  = normalized from/to coords
    4     = capture
    5..9  = special one-hot: normal, double, KingCastle, QueenCastle, en_passant
    10..14 = promotion one-hot: none, N, B, R, Q
    """
    feats = np.zeros(15, dtype=np.float32)

    feats[0] = action.from_row / 13.0
    feats[1] = action.from_col / 13.0
    feats[2] = action.to_row / 13.0
    feats[3] = action.to_col / 13.0
    target = board.board_state[action.to_row][action.to_col]
    if target != 0 or action.special == "en_passant":
        feats[4] = 1.0

    special_map = {
        None: 0,
        "double": 1,
        "KingCastle": 2,
        "QueenCastle": 3,
        "en_passant": 4,
    }
    promotion_map = {
        None: 0,
        "N": 1,
        "B": 2,
        "R": 3,
        "Q": 4,
    }

    feats[5 + special_map.get(action.special, 0)] = 1.0
    feats[10 + promotion_map.get(action.promotion, 0)] = 1.0
    return feats


class MoveScorer(nn.Module):
    def __init__(self, state_size=29 * 14 * 14, action_size=15):
        super().__init__()
        state_out = 256
        action_out = 64
        self.state_net = nn.Sequential(
            nn.Linear(state_size, 512),
            nn.ReLU(),
            nn.Linear(512, state_out),
            nn.ReLU(),
        )
        self.action_net = nn.Sequential(
            nn.Linear(action_size, 64),
            nn.ReLU(),
            nn.Linear(64, action_out),
            nn.ReLU(),
        )
        self.head = nn.Sequential(
            nn.Linear(state_out + action_out, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
        )

    def forward(self, state_batch, action_batch):
        s = self.state_net(state_batch)
        a = self.action_net(action_batch)
        x = torch.cat([s, a], dim=-1)
        return self.head(x).squeeze(-1)


class RLAgent:
    def __init__(self, model: MoveScorer, epsilon=0.1, gamma=0.99, lr=1e-3, buffer_capacity=10000):
        self.model = model                      
        self.target_model = copy.deepcopy(model)
        # Exploration
        self.epsilon = epsilon                 
        self.gamma = gamma
        self.wins=0
        self.train_steps = 0
        self.target_update_steps = 200
        self.optimizer = optim.Adam(model.parameters(), lr=lr)
        self.buffer = ReplayBuffer(capacity=buffer_capacity)
        self.loss_fn = nn.MSELoss()
        
    def store(self, state, action, reward, next_state,next_actions, done):
        self.buffer.add(state, action, reward, next_state, next_actions, done)
    
    def train_from_buffer(self, batch_size=32):
        if len(self.buffer) < batch_size:
            return None

        batch = self.buffer.sample(batch_size)
        
        loss = self.train_batch(batch)
        
        self.train_steps += 1
        if self.train_steps % self.target_update_steps == 0:
            self.target_model.load_state_dict(self.model.state_dict())
        
        return loss
    
    def select_action(self, board: Board):
        # Epsilon greedy
        player = board.current_player_index
        actions = board.get_all_moves(player)

        if not actions:
            print("Error, player alive, but no actions")
            return None

        # --- Exploration ---
        if random.random() < self.epsilon:
            return random.choice(actions)

        # --- Exploitation ---
        state = board.encode_state()
        state_tensor = torch.tensor(state.flatten(), dtype=torch.float32)

        action_features = []
        for a in actions:
            feats = action_to_features(a, board)
            action_features.append(feats)

        action_tensor = torch.from_numpy(np.array(action_features)).float()

        # Repeat state for each action
        state_batch = state_tensor.unsqueeze(0).repeat(len(actions), 1)

        # Score all actions
        with torch.no_grad():
            q_values = self.model(state_batch, action_tensor)

        # Pick best action
        best_idx = torch.argmax(q_values).item()
        return actions[best_idx]

    def train_batch(self, batch):

        #batch elements:(state, action_features, reward, next_state, next_action_features, done)
        
        states = []
        actions = []
        targets = []

        for state, action_feats, reward, next_state, next_action_feats, done in batch:
            states.append(state.flatten())
            actions.append(action_feats)

            if done:
                target = reward
            else:
                # next_action_feats is already stored: shape (num_next_actions, 15)
                next_state_tensor = torch.tensor(next_state.flatten(), dtype=torch.float32)
                next_action_tensor = torch.from_numpy(np.array(next_action_feats)).float()

                # repeat next_state for each possible next action
                next_state_batch = next_state_tensor.unsqueeze(0).repeat(len(next_action_feats), 1)
                
                with torch.no_grad():
                    next_q_values = self.target_model(next_state_batch, next_action_tensor)

                max_next_q = torch.max(next_q_values).item()
                target = reward + self.gamma * max_next_q

            targets.append(target)

        # Convert to tensors for batch training
        state_tensor = torch.from_numpy(np.asarray(states, dtype=np.float32))
        action_tensor = torch.from_numpy(np.array(actions)).float()
        target_tensor = torch.from_numpy(np.asarray(targets, dtype=np.float32))

        # Compute current Q-values
        q_values = self.model(state_tensor, action_tensor)

        # Loss and backprop
        loss = self.loss_fn(q_values, target_tensor)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        return loss.item()
    
    
    
    
def play_one_game(env: Chess4Env, agent: RLAgent, train=True, max_moves=200, save=None):
    env.reset()
    done = False

    while not done:
        board = env.board
        current_player = board.current_player_index

        if current_player==1:
            action = agent.select_action(board)
        else:
            action=board.get_random_action(current_player)

        if action is None:
            print("none action error")
            break
        action_features = action_to_features(action, board) 
        state=board.encode_state()
        next_state, reward, done, _ = env.step(action)
        next_actions = board.get_all_moves(board.current_player_index)
        if not next_actions:
            return None
        next_action_features = [
        action_to_features(a, board)
        for a in next_actions
        ]
        agent.store(state,action_features,reward,next_state,next_action_features,done)

        if train and current_player==1:
            agent.train_from_buffer(batch_size=32)


        if board.move_number >= max_moves:
            done=True
            print("Match ended in draw")
            break


    winner = env.board.get_winner()
    if save is not None:
        env.board.save_actions(save)
    return winner    

def train_agent(num_episodes=100):
    env = Chess4Env()
    model = MoveScorer()
    agent = RLAgent(model)
    win_count = [0,0,0,0]

    for episode in range(num_episodes):
        if episode %50==49:
            winner = play_one_game(
            env,
            agent,
            train=True,
            max_moves=200,
            save=f"./saves/1agent/trial5/match{episode//50}.txt"
        )
        else:
            winner = play_one_game(env, agent, train=True)
        if winner is not None:
            win_count[winner-1]+=1



        agent.epsilon = max(0.05, agent.epsilon * 0.995)
        #agent.epsilon = max(0.05, agent.epsilon * 0.999)
        # --- Log ---
        if (episode + 1) % 50 == 0:
            print("----------------------------")
            print(f"Episode {episode+1}, epsilon: {agent.epsilon:.3f}")
            print(f"player1 winrate: {win_count[0]/50:.2f}")
            print(f"player2 winrate: {win_count[1]/50:.2f}")
            print(f"player3 winrate: {win_count[2]/50:.2f}")
            print(f"player4 winrate: {win_count[3]/50:.2f}")
            print("----------------------------")
            
            win_count = [0,0,0,0]

    return agent

def evaluate_agent(agent, games=100):
    env = Chess4Env()
    wins = [0,0,0,0]

    old_epsilon = agent.epsilon
    agent.epsilon = 0.0  # nincs random

    for i in range(games):
        if i %20==19:
            winner = play_one_game(
            env,
            agent,
            train=False,
            max_moves=200,
            save=f"./saves/1agent/trial5/match{i//20}.txt"
        )
        else:
            winner = play_one_game(env, agent, train=False)
        if winner is not None:
            wins[winner-1]+=1

    agent.epsilon = old_epsilon
    print("----------------------------")
    print(f"Evaluation:")
    print(f"player1 winrate: {wins[0]/games:.2f}")
    print(f"player2 winrate: {wins[1]/games:.2f}")
    print(f"player3 winrate: {wins[2]/games:.2f}")
    print(f"player4 winrate: {wins[3]/games:.2f}")
    print("----------------------------")

def initgamestart():
    player1=Player(1,"","")
    player2=Player(2,"","")
    player3=Player(3,"","")
    player4=Player(4,"","")
    board=Board(player1, player2, player3, player4)
    return board
    

    
    
def mutate_agent(base_agent: RLAgent, noise_std=0.01):
    new_model = copy.deepcopy(base_agent.model)

    for param in new_model.parameters():
        param.data += torch.randn_like(param) * noise_std

    return RLAgent(new_model)

def repopulate(top_agents, total_size, noise_std=0.01):
    #keep 2 best
    # replace others with mutations of top half
    new_population = []
    elite_count = max(2, len(top_agents) // 4)
    new_population.extend(top_agents[:elite_count])
    #save the best agents for later reuse
    for i in top_agents[:elite_count]:   
        torch.save(i.model.state_dict(), f"hall_of_fame/trial4/league_agent_{uuid.uuid4()}.pth")

    while len(new_population) < total_size:
        parent = random.choice(top_agents)
        child = mutate_agent(parent, noise_std)
        # hyperparam noise
        child.epsilon = np.clip(parent.epsilon + np.random.randn()*0.01, 0.01, 0.5)
        child.gamma   = np.clip(parent.gamma   + np.random.randn()*0.01, 0.8, 0.99)
        new_population.append(child)

    return new_population

def evolve_population(population):
    # rank agents
    scored = [(agent, agent.wins) for agent in population]

    scored.sort(key=lambda x: x[1], reverse=True)

    top = [a for a, _ in scored[:len(population)//2]]

    return repopulate(top, len(population))

def train_league(num_agents=16, episodes=500, max_moves=200):
    base_model = MoveScorer()
    base_agent = RLAgent(base_model)
    # train a base agent against 3 random, to learn some moves
    base_agent = train_agent(50)
    population = []
    for _ in range(num_agents):
        population.append(mutate_agent(base_agent, noise_std=0.01))

    env = Chess4Env()

    for episode in range(episodes):

        # pick 4 random agents
        players = random.sample(population, 4)

        env.reset()
        done = False

        while not done:
            board = env.board
            if env.board.is_game_over:
                break
            current_player = board.current_player_index

            agent = players[current_player - 1]
            before_state = board.encode_state()

            action = agent.select_action(board)

            if action is None:
                print("action was none error")
                break
            action_features = action_to_features(action, board) 
            
            next_state, reward, done, _ = env.step(action)
            next_actions = board.get_all_moves(board.current_player_index)
            next_action_features = [
            action_to_features(a, board)
            for a in next_actions
            ]
            agent.store(before_state,action_features,reward,next_state,next_action_features,done)
            #train agents
            if len(agent.buffer) > 32 and env.board.move_number % 4 == 0:
                agent.train_from_buffer(batch_size=32)
            
            if board.move_number >= max_moves:
                done=True
                print("match ended in draw")
                break

            
        winner = env.board.get_winner()

        if winner is not None:
            players[winner - 1].wins += 1
        #
        if episode % 50 == 49 and episode >0:
             save=f"./saves/league/trial4/match{episode//50}.txt"
             env.board.save_actions(save)
        # periodic evolution
        #reset wins and print scoreboard
        if episode % 100 == 99 and episode > 0:
            scoreboard(population)
            population = evolve_population(population)
            zero_wins(population)

        if episode % 100 == 99:
            print(f"Episode {episode}")
        
        for agent in population:
            agent.epsilon = max(0.05, agent.epsilon * 0.995)
            
def scoreboard(population):
    print("--------scoreboard:-----------")
    for i in population:
        print(i.wins)
    print("--------------------------------")
    
def zero_wins(population):
    for i in population:
        i.wins=0
        
        
        
if __name__ == "__main__":
    train_league(16,500)