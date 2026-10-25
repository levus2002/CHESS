import csv
import random
from pathlib import Path

import numpy as np
import torch

from RL.AgentStorage import AgentStorage
from RL.DQNActionProvider import DQNActionProvider
from RL.MatchRunner import MatchRunner


class Benchmark:
    def __init__(
        self,
        baseline_path="agents/dqn_800.pt",
        device="cpu",
        matches_per_agent=40,
        baseline_epsilon=0.05,
        seed=42,
    ):
        if matches_per_agent <= 0 or matches_per_agent % 4 != 0:
            raise ValueError("matches_per_agent must be a positive multiple of 4")

        self.baseline_path = baseline_path
        self.device = device
        self.matches_per_agent = matches_per_agent
        self.baseline_epsilon = baseline_epsilon
        self.seed = seed

        self.baseline_agents = [
            AgentStorage.load(baseline_path, device=device)
            for _ in range(3)
        ]

    def evaluate(self, agent_path):
        candidate = AgentStorage.load(str(agent_path), device=self.device)

        wins = 0
        draws = 0
        losses = 0

        for match_index in range(self.matches_per_agent):
            # Each checkpoint receives the same seed schedule.
            match_seed = self.seed + match_index

            random.seed(match_seed)
            np.random.seed(match_seed)
            torch.manual_seed(match_seed)

            # Rotate candidate through all four seats.
            candidate_seat = (match_index % 4) + 1

            providers = {}
            baseline_index = 0

            for player_id in range(1, 5):
                if player_id == candidate_seat:
                    providers[player_id] = DQNActionProvider(
                        candidate,
                        epsilon=0.0,
                    )
                else:
                    providers[player_id] = DQNActionProvider(
                        self.baseline_agents[baseline_index],
                        epsilon=self.baseline_epsilon,
                    )
                    baseline_index += 1

            result = MatchRunner(
                providers=providers,
                learning_players=set(),
            ).play_game()

            if result.winner_id == candidate_seat:
                wins += 1
            elif (
                result.winner_id is None
                and candidate_seat in result.survivors
            ):
                draws += 1

            else:
                losses += 1

        score = (wins + 0.25 * draws) / self.matches_per_agent

        return {
            "agent": str(agent_path),
            "matches": self.matches_per_agent,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "score": score,
        }

    def evaluate_directory(self, directory):
        directory = Path(directory)

        checkpoints = sorted(directory.glob("generation_*_best.pt"))

        if not checkpoints:
            print(f"No checkpoints found in {directory}")
            return []

        results = []

        for index, checkpoint in enumerate(checkpoints, start=1):
            print(f"[{index}/{len(checkpoints)}] {checkpoint.name}")

            result = self.evaluate(checkpoint)
            results.append(result)

            print(
                f"  W: {result['wins']} | "
                f"D: {result['draws']} | "
                f"L: {result['losses']} | "
                f"Score: {result['score']:.3f}"
            )

        return results

    def evaluate_trials(self, trials, output_path):
        all_results = []

        for trial in trials:
            print(f"\n===== {trial} =====")
            all_results.extend(self.evaluate_directory(trial))

        if not all_results:
            return []

        all_results.sort(
            key=lambda result: result["score"],
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
            writer.writerows(all_results)

        print(f"\nResults saved to: {output_path}")

        print("\n===== TOP 5 =====")
        for result in all_results[:5]:
            print(
                f"{result['agent']} | "
                f"Score: {result['score']:.3f}"
            )

        return all_results


def main():
    benchmark = Benchmark(
        #baseline_path="agents/dqn_800.pt",
        baseline_path="agents/evolution/trial_002/generation_008_best.pt",
        device="cuda",
        matches_per_agent=40,
        baseline_epsilon=0.05,
        seed=42,
    )

    benchmark.evaluate_trials(
        trials=[
            "agents/evolution/trial_002",
            "agents/evolution/trial_003",
            "agents/evolution/trial_004",
        ],
        output_path="agents/evolution/benchmarks/results.csv",
    )


if __name__ == "__main__":
    main()