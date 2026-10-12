
from dataclasses import dataclass

import numpy as np

from Model.GameModel import GameModel
from Persistence.Player import Player
from Persistence.Board import Board
from RL.Encoding import encode_state, encode_action
from RL.ReplayBuffer import Experience
from RL.Rewards import Rewards


@dataclass
class MatchResult:
    winner_id: int | None
    move_count: int
    experiences: list[Experience]
    actions: list


@dataclass
class PendingExperience:
    state: np.ndarray
    action: np.ndarray
    reward: float = 0.0


class MatchRunner:
    def __init__(
        self,
        providers: dict,
        learning_players: set[int] | None = None,
        max_turns: int = 100,
    ):
        self.providers = providers
        self.learning_players = set(learning_players or [])
        self.max_turns = max_turns

    def play_game(self) -> MatchResult:
        
        board = Board()
        players = {
            player_id: Player(player_id)
            for player_id in range(1, 5)
        }

        game = GameModel(board, players)
        game.max_turns = self.max_turns
        game.new_game()

        experiences = []
        pending = {}

        while not game.isgameover:
            player_id = game.current_player
            provider = self.providers[player_id]

            if player_id in self.learning_players:
                state = encode_state(game, player_id)

                legal_actions = game.movegen.get_all_moves(
                    game.players[player_id].Figures
                )
                encoded_actions = [
                    encode_action(game, action)
                    for action in legal_actions
                ]

                # Finish the previous transition for this player.
                if player_id in pending:
                    previous = pending.pop(player_id)
                    experiences.append(
                        Experience(
                            state=previous.state,
                            action=previous.action,
                            reward=previous.reward,
                            next_state=state,
                            next_actions=encoded_actions,
                            done=False,
                        )
                    )

                action = provider.get_action(game)

                # Encode before executing the action.
                pending[player_id] = PendingExperience(
                    state=state,
                    action=encode_action(game, action),
                )
            else:
                action = provider.get_action(game)

            result = game.step(action)

            # Immediate rewards belong to the acting player.
            if player_id in pending:
                pending[player_id].reward += Rewards.move_reward(result)

            # Close experiences for newly eliminated players.
            for pid in list(pending):
                if game.players[pid].IsDefeated:
                    previous = pending.pop(pid)
                    experiences.append(
                        Experience(
                            state=previous.state,
                            action=previous.action,
                            reward=previous.reward,
                            next_state=None,
                            next_actions=[],
                            done=True,
                        )
                    )

        # Distribute final rewards before closing remaining experiences.
        terminal_rewards = Rewards.terminal_rewards(game)

        for pid, previous in pending.items():
            experiences.append(
                Experience(
                    state=previous.state,
                    action=previous.action,
                    reward=previous.reward + terminal_rewards[pid],
                    next_state=None,
                    next_actions=[],
                    done=True,
                )
            )

        return MatchResult(
            winner_id=game.winner_id,
            move_count=game.move_number,
            experiences=experiences,
            actions=list(game.action_history),
        )
