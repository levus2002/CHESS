
from Model.GameModel import GameModel
from RL.DQNAgent import DQNAgent
from RL.Encoding import encode_state, encode_action


class DQNActionProvider:
    def __init__(self, agent: DQNAgent, epsilon: float = 0.2):
        self.agent = agent
        self.epsilon = epsilon

    def get_action(self, game: GameModel):
        player_id = game.current_player
        actions = game.movegen.get_all_moves(
            game.players[player_id].Figures
        )

        state = encode_state(game, player_id)
        encoded_actions = [
            encode_action(game, action) for action in actions
        ]

        index = self.agent.select_action(
            state, encoded_actions, epsilon=self.epsilon
        )
        return actions[index]
