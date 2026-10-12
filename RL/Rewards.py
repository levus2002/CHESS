

from dataclasses import dataclass

from Model.GameModel import GameModel
from Model.Dataclasses import MoveResult


class Rewards:
    CAPTURE_SCALE = 0.01
    PROMOTION_SCALE = 0.01
    WIN_REWARD = 1.0
    DRAW_REWARD_POOL = 0.36

    @staticmethod
    def move_reward(result: MoveResult) -> float:
        reward = 0.0

        if result.captured_player_active:
            reward += Rewards.CAPTURE_SCALE * result.captured_value

        if result.promotion_value:
            reward += Rewards.PROMOTION_SCALE * (result.promotion_value - 1)

        return reward

    @staticmethod
    def terminal_rewards(game: GameModel) -> dict[int, float]:
        rewards = {player_id: 0.0 for player_id in game.players}

        if not game.isgameover:
            return rewards

        if game.winner_id is not None:
            rewards[game.winner_id] = Rewards.WIN_REWARD
            return rewards

        survivors = [
            player_id
            for player_id, player in game.players.items()
            if not player.IsDefeated
        ]

        if survivors:
            draw_reward = Rewards.DRAW_REWARD_POOL / len(survivors)

            for player_id in survivors:
                rewards[player_id] = draw_reward

        return rewards