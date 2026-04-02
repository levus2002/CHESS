from Persistence.Board import Board
from Persistence.Player import Player
import json


class Chess4Env:
    def __init__(self):
        self.board = initgamestart()
        self.rewards=[[] for _ in range(4)]

    def reset(self):
        self.board.newgame()
        self.rewards=[[] for _ in range(4)]
        return self.board.encode_state()

    def step(self, action):
        current_player = self.board.current_player_index
        self.board.make_move(action)
        reward = self.board.get_reward(current_player)
        self.rewards[current_player-1].append(reward)
        self.board.reset_reward(current_player) 
        done = self.board.is_game_over
        next_state = self.board.encode_state()
        info = {"current_player": self.board.current_player_index, "msg": self.board.msg}
        if done:
            self.board.get_player(self.board.get_winner).Reward+=1
        return next_state, reward, done, info
    
    

    def play_random_game(self, max_moves=200):
        self.reset()
        finished_in_time=True
        while not self.board.is_game_over:
            current_player = self.board.current_player_index

            action = self.board.get_random_action(current_player)
            next_state, reward, done, info=self.step(action)
            if done:
                break
            
            
            if self.board.move_number >= max_moves:
                print("Reached move limit → draw")
                finished_in_time=False
                break

        print("Game finished")
        print("Moves:", self.board.move_number)
        self.statistics(self.board.move_number,"4random")
        return finished_in_time
    
    def statistics(self,turn_count,match_type):
        filename,p1control,p2control,p3control,p4control=self.get_controls(match_type)
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
        self.save_game_stats(filename,game_stats)
    
    def get_controls(self,type):
        match type:
            case "4random":
                return  ("./4rand.jsonl","random","random","random","random")
            case "1agent":
                return ("./1agent.jsonl","agent","random","random","random")
            case "4agent":
                return ("./4agent.jsonl","agent","agent","agent","agent")
        
    def save_game_stats(self,filename, stats):
        with open(filename, "a") as f:
            f.write(json.dumps(stats) + "\n")

    

def initgamestart():
        player1=Player(1,"","")
        player2=Player(2,"","")
        player3=Player(3,"","")
        player4=Player(4,"","")
        board=Board(player1, player2, player3, player4)
        return board
    
if __name__ == "__main__":
    counter=0
    for i in range(5):
        print(f"\n=== Game {i+1} ===")
        if Chess4Env().play_random_game():
            counter=counter+1
    print(counter)
        