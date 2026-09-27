from ui.base import UIElement
from Model.GameModel import GameModel

import pygame as pg
import pygame.freetype as ft


class StatusBar(UIElement):
    def __init__(self, rect: pg.Rect, game_model: GameModel):
        super().__init__(rect)

        self.game_model = game_model
        self.message = ""
        self.font = ft.SysFont(None, 18)

    def render(self, surf: pg.Surface) -> None:
        pg.draw.rect(surf, (30, 30, 30), self.rect)

        player = self.game_model.players[
            self.game_model.current_player
        ]

        text = (
            f"Turn: Player {player.Which_Player} "
            f"({player.Color}) | "
            f"Move: {self.game_model.move_number}"
        )

        self.font.render_to(
            surf,
            (self.rect.x + 8, self.rect.y + 10),
            text,
            fgcolor=(230, 230, 230)
        )

        if self.message:
            self.font.render_to(
                surf,
                (self.rect.centerx, self.rect.y + 10),
                self.message,
                fgcolor=(230, 230, 230)
            )