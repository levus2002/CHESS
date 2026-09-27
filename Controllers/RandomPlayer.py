from Model.Action import Action
from Model.GameModel import GameModel
    
import random

class RandomPlayer:
    def get_action(self, game: GameModel) -> Action:
        player = game.CurrentPlayer()
        actions = []

        for figure in player.Figures:
            actions.extend(
                game.movegen.get_possible_moves(figure)
            )

        if not actions:
            raise RuntimeError("No available actions")

        return random.choice(actions)