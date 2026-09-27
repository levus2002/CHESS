import pygame as pg

class UIElement:
    def __init__(self, rect: pg.Rect):
        self.rect = rect

    def handle_event(self, ev: pg.event.Event) -> None:
        pass

    def update(self, dt: int) -> None:
        pass

    def render(self, surf: pg.Surface) -> None:
        pass