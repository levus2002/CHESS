
import copy
import random
from dataclasses import dataclass
from pathlib import Path

import torch

from RL.AgentStorage import AgentStorage
from RL.DQNAgent import DQNAgent
from RL.DQNActionProvider import DQNActionProvider
from RL.DQNTrainer import DQNTrainer
from RL.MatchRunner import MatchRunner
from RL.ReplayBuffer import ReplayBuffer
import csv

@dataclass
class PopulationMember:
    agent: DQNAgent
    trainer: DQNTrainer
    buffer: ReplayBuffer
    fitness: float = 0.0
    matches_played: int = 0
    wins: int = 0
    draws: int = 0


class EvolutionTrainer:
    def __init__(
        self,
        base_model_path: str,
        population_size: int = 16,
        mutation_std: float = 0.005,
        device: str = "cpu",
    ):
        if population_size < 4:
            raise ValueError("Population must contain at least 4 agents.")
        self.base_model_path = base_model_path
        self.device = device
        self.mutation_std = mutation_std
        self.population: list[PopulationMember] = []

        base_agent = AgentStorage.load(base_model_path, device=device)

        for _ in range(population_size):
            model = copy.deepcopy(base_agent.model)
            self._mutate(model)
            self.population.append(self._create_member(model))

    def _create_member(self, model) -> PopulationMember:
        agent = DQNAgent(model, device=self.device)
        buffer = ReplayBuffer()

        trainer = DQNTrainer(
            model=model,
            buffer=buffer,
            device=self.device,
        )

        return PopulationMember(
            agent=agent,
            trainer=trainer,
            buffer=buffer,
        )

    def _mutate(self, model):
        with torch.no_grad():
            for parameter in model.parameters():
                parameter.add_(
                    torch.randn_like(parameter) * self.mutation_std
                )

    def play_match(
        self,
        epsilon: float = 0.2,
        training: bool = True,
        training_steps: int = 1,
    ) -> int | None:
        selected = random.sample(self.population, 4)

        providers = {
            player_id: DQNActionProvider(
                member.agent,
                epsilon=epsilon,
            )
            for player_id, member in enumerate(selected, start=1)
        }

        runner = MatchRunner(
            providers=providers,
            learning_players={1, 2, 3, 4} if training else set(),
        )

        result = runner.play_game()

        if training:
            for player_id, member in enumerate(selected, start=1):
                for experience in result.experiences[player_id]:
                    member.buffer.add(
                        state=experience.state,
                        action=experience.action,
                        reward=experience.reward,
                        next_state=experience.next_state,
                        next_actions=experience.next_actions,
                        done=experience.done,
                    )

                for _ in range(training_steps):
                    member.trainer.train_step()

        else:
            # Fitness is calculated only during evaluation.
            for player_id, member in enumerate(selected, start=1):
                member.matches_played += 1

                if result.winner_id == player_id:
                    member.wins += 1
                    member.fitness += 1.0

                elif (
                    result.winner_id is None
                    and player_id in result.survivors
                ):
                    member.draws += 1
                    member.fitness += 0.25

        return result.winner_id

    def _reset_fitness(self):
        for member in self.population:
            member.fitness = 0.0
            member.matches_played = 0
            member.wins = 0
            member.draws = 0

    def _rank_population(self) -> list[PopulationMember]:
        return sorted(
            self.population,
            key=lambda member: (
                member.fitness / member.matches_played
                if member.matches_played else 0.0
            ),
            reverse=True,
        )

    def _evolve(self, elite_count: int = 4, parent_count: int = 8):
        ranked = self._rank_population()

        elites = ranked[:elite_count]
        parents = ranked[:parent_count]

        next_population = list(elites)

        while len(next_population) < len(self.population):
            parent = random.choice(parents)

            model = copy.deepcopy(parent.agent.model)
            self._mutate(model)

            next_population.append(self._create_member(model))

        self.population = next_population
        self._reset_fitness()

    def train(
        self,
        generations: int = 10,
        training_matches: int = 400,
        evaluation_matches: int = 100,
        epsilon: float = 0.2,
        training_steps: int = 1,
        elite_count: int = 4,
        parent_count: int = 8,
        output_dir: str = "agents/evolution",
    ):
        if not 1 <= elite_count <= parent_count <= len(self.population):
            raise ValueError("Invalid elite/parent counts.")

        output_path = self.next_trial_directory(output_dir)
        print(f"Saving results to: {output_path}")
        results_path = output_path / "results.csv"

        with results_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "generation",
                "best_fitness",
                "average_fitness",
                "benchmark_wins",
                "benchmark_draws",
                "benchmark_losses",
            ])

        for generation in range(1, generations + 1):
            print(f"\n===== Generation {generation}/{generations} =====")

            self._reset_fitness()

            # Phase 1: DQN training
            for match_number in range(1, training_matches + 1):
                self.play_match(
                    epsilon=epsilon,
                    training=True,
                    training_steps=training_steps,
                )

                if match_number % 50 == 0:
                    print(
                        f"Training: {match_number}/{training_matches}"
                    )

            # Phase 2: evaluation, no exploration or training
            for match_number in range(1, evaluation_matches + 1):
                self.play_match(
                    epsilon=0.0,
                    training=False,
                )

            ranked = self._rank_population()
            best = ranked[0]
            
            best_fitness = (
                best.fitness / best.matches_played
                if best.matches_played else 0.0
            )

            average_fitness = sum(
                member.fitness / member.matches_played
                if member.matches_played else 0.0
                for member in self.population
            ) / len(self.population)

            print(
                f"Evaluation | "
                f"Best fitness: {best_fitness:.3f} | "
                f"Average fitness: {average_fitness:.3f} | "
                f"Best wins: {best.wins}/{best.matches_played}"
            )


            # Save the best model before reproduction.
            AgentStorage.save(
                best.agent,
                str(
                    output_path
                    / f"generation_{generation:03d}_best.pt"
                ),
            )

            if generation < generations:
                self._evolve(
                    elite_count=elite_count,
                    parent_count=parent_count,
                )
                

    @staticmethod
    def next_trial_directory(base_dir: str) -> Path:
        base_path = Path(base_dir)
        base_path.mkdir(parents=True, exist_ok=True)

        trial_number = 1

        while True:
            trial_path = base_path / f"trial_{trial_number:03d}"

            try:
                trial_path.mkdir(exist_ok=False)
                return trial_path
            except FileExistsError:
                trial_number += 1


def main():
    evolution = EvolutionTrainer(
        base_model_path="agents/evolution/trial_002/generation_008_best.pt",
        population_size=16,
        mutation_std=0.002,
        device="cuda",
    )

    evolution.train(
        generations=4,
        training_matches=1100,
        evaluation_matches=150,
        epsilon=0.2,
        training_steps=4,
        elite_count=4,
        parent_count=8,
        output_dir="agents/evolution",
    )


if __name__ == "__main__":
    main()
