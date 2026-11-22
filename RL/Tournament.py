import csv
import itertools
import math
import random
from pathlib import Path

import numpy as np
import torch

from RL.AgentStorage import AgentStorage
from RL.DQNActionProvider import DQNActionProvider
from RL.MatchRunner import MatchRunner


class Tournament:
    def __init__(self, device="cuda", epsilon=0.0, seed=42):
        self.device = device
        self.epsilon = epsilon
        self.seed = seed

    def evaluate(self, agents, output_path="agents/evolution/tournaments/results.csv"):
        paths = [str(Path(path)) for path in agents]

        if len(paths) < 4:
            raise ValueError("A tournament needs at least 4 agents")
        
        models = [
            AgentStorage.load(path, device=self.device)
            for path in paths
        ]

        stats = [
            {
                "agent": path,
                "matches": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
            }
            for path in paths
        ]

        total = math.comb(len(paths), 4) * 6
        completed = 0

        print(f"{len(paths)} agents | {total} matches")
        seating_rng = random.Random(self.seed)
        with torch.inference_mode():
            for group in itertools.combinations(range(len(paths)), 4):

                # Six permutations:
                for others in itertools.permutations(group[1:]):
                    seating = (group[0],) + others
                    #so the fixed agent is not always seat 1
                    shift = seating_rng.randrange(4)
                    seating = seating[shift:] + seating[:shift]

                    game_seed = self.seed + completed
                    random.seed(game_seed)
                    np.random.seed(game_seed % (2**32))
                    torch.manual_seed(game_seed)

                    providers = {
                        seat: DQNActionProvider(
                            models[index],
                            epsilon=self.epsilon,
                        )
                        for seat, index in enumerate(seating, start=1)
                    }

                    result = MatchRunner(
                        providers=providers,
                        learning_players=set(),
                    ).play_game()

                    winner = result.winner_id

                    for seat, index in enumerate(seating, start=1):
                        record = stats[index]
                        record["matches"] += 1

                        if winner is None and seat in result.survivors:
                            record["draws"] += 1
                        elif winner == seat:
                            record["wins"] += 1
                        else:
                            record["losses"] += 1

                    completed += 1

                    if completed % 100 == 0 or completed == total:
                        print(f"{completed}/{total} matches")

        for record in stats:
            record["score"] = (
                record["wins"] + 0.25 * record["draws"]
            ) / record["matches"]

        stats.sort(
            key=lambda record: record["score"],
            reverse=True,
        )

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "agent",
                    "matches",
                    "wins",
                    "draws",
                    "losses",
                    "score",
                ],
            )
            writer.writeheader()
            writer.writerows(stats)

        print("\n===== TOURNAMENT RESULTS =====")

        for rank, record in enumerate(stats, start=1):
            print(
                f"{rank}. {record['agent']} | "
                f"W: {record['wins']} | "
                f"D: {record['draws']} | "
                f"L: {record['losses']} | "
                f"Score: {record['score']:.3f}"
            )

        print(f"\nResults saved to: {output_path}")

        return stats


def main():
    tournament = Tournament(
        device="cuda",
        epsilon=0.02,
        seed=42,
    )

    tournament.evaluate(
        agents=[
            "agents/evolution/trial_006/generation_001_best.pt",

            "agents/evolution/trial_006/generation_002_best.pt",

            "agents/evolution/trial_007/generation_003_best.pt",
            
            "agents/evolution/trial_007/generation_004_best.pt",

            "agents/evolution/trial_008/generation_002_best.pt",

            "agents/evolution/trial_010/generation_003_best.pt",
            
            "agents/evolution/trial_009/generation_001_best.pt",

            "agents/evolution/trial_009/generation_003_best.pt",

            "agents/evolution/trial_004/generation_010_best.pt",
            
            "agents/evolution/trial_004/generation_007_best.pt",

            "agents/evolution/trial_011/generation_002_best.pt",
            
            "agents/evolution/trial_013/generation_003_best.pt",
            "agents/evolution/trial_012/generation_003_best.pt",
            "agents/evolution/trial_013/generation_004_best.pt",
            "agents/evolution/trial_014/generation_003_best.pt",
            "agents/evolution/trial_012/generation_001_best.pt",

        ],
        output_path="agents/evolution/tournaments/bestchangedbig002results.csv",
    )


if __name__ == "__main__":
    main()