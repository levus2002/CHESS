from ui.base import UIElement
import pygame as pg
import pygame.freetype as ft
from collections.abc import Callable


class MenuBar(UIElement):
    def __init__(
        self,
        rect: pg.Rect,
        buttons: list[str],
        callbacks: dict[str, Callable[[], None]] | None = None,
    ):
        super().__init__(rect)

        self.buttons = buttons
        self.callbacks = callbacks or {}
        self.button_rects: dict[str, pg.Rect] = {}

        self.font = ft.SysFont(None, 18)
        self.icon_font = ft.SysFont("Segoe UI Symbol", 20)


    def handle_event(self, ev: pg.event.Event) -> None:
        if ev.type != pg.MOUSEBUTTONDOWN or ev.button != 1:
            return

        for name, rect in self.button_rects.items():
            if rect.collidepoint(ev.pos):
                callback = self.callbacks.get(name)

                if callback is not None:
                    callback()

                return

    def render(self, surf: pg.Surface) -> None:
        pg.draw.rect(surf, (50, 50, 50), self.rect)

        self.button_rects.clear()

        gap = 8
        x = self.rect.x + 10
        y = self.rect.y + 10
        btn_h = 32

        for name in self.buttons:
            btn_w = self.font.get_rect(name).width + 16
            rect = pg.Rect(x, y, btn_w, btn_h)

            pg.draw.rect(
                surf, (70, 70, 70),
                rect, border_radius=4
            )

            self.font.render_to(
                surf, (x + 8, y + 6),
                name, fgcolor=(230, 230, 230)
            )

            self.button_rects[name] = rect
            x += btn_w + gap
