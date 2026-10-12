from typing import Protocol

from Model.GameModel import GameModel
from Model.Dataclasses import Action

class ActionProvider(Protocol):
    def get_action(self, game: GameModel) -> Action:
        ...