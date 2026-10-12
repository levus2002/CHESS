
from RL.MoveScorer import MoveScorer
from RL.DQNAgent import DQNAgent
from RL.DQNTrainer import DQNTrainer
from RL.DQNActionProvider import DQNActionProvider
from RL.ReplayBuffer import ReplayBuffer
from RL.MatchRunner import MatchRunner
from Controllers.RandomPlayer import RandomPlayer
from RL.AgentStorage import AgentStorage

def main():
    model = MoveScorer()
    buffer = ReplayBuffer(capacity=50000)

    agent = DQNAgent(model)
    trainer = DQNTrainer(
        model=model,
        buffer=buffer,
        batch_size=64,
    )

    dqn_provider = DQNActionProvider(agent, epsilon=0.2)

    providers = {
        1: dqn_provider,
        2: RandomPlayer(),
        3: RandomPlayer(),
        4: RandomPlayer(),
    }

    runner = MatchRunner(
        providers=providers,
        learning_players={1},
        max_turns=100,
    )

    wins = 0
    draws = 0
    training_matches=800
    eval_matches=100
    total_matches=training_matches+eval_matches
    for match_number in range(1, total_matches+1):
        if match_number == training_matches + 1:
            AgentStorage.save(agent, "agents/dqn_800.pt")
            dqn_provider.epsilon = 0.0
        result = runner.play_game()

        for experience in result.experiences:
            buffer.add(
                experience.state,
                experience.action,
                experience.reward,
                experience.next_state,
                experience.next_actions,
                experience.done,
            )
            
        
        
        # Train after each match, once enough experiences exist.
        if match_number<training_matches+1:
            loss = trainer.train_step()
        else:
            loss = None

        if result.winner_id == 1:
            wins += 1
        elif result.winner_id is None:
            draws += 1

        loss_text = f"{loss:.4f}" if loss is not None else "waiting"

        print(
            f"Match {match_number:3d}/{total_matches} | "
            f"Rounds: {result.move_count:4d} | "
            f"Winner: {result.winner_id} | "
            f"DQN wins: {wins:3d} | "
            f"Draws: {draws:3d} | "
            f"Buffer: {len(buffer):5d} | "
            f"Loss: {loss_text}",
            flush=True,
        )

    print(f"\nDQN win rate: {wins / 100:.1%}")


if __name__ == "__main__":
    main()
