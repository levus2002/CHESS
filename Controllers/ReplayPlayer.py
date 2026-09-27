from Model.Action import Action
from Model.GameModel import GameModel

class ReplayPlayer:
    def __init__(self, actions: list[Action]):
        self.actions = iter(actions)

    def get_action(self, game: GameModel) -> Action:
        return next(self.actions)