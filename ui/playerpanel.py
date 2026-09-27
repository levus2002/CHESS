
from collections.abc import Callable

import pygame as pg
import pygame.freetype as ft

from ui.base import UIElement


COLORS = {
    "red": (220, 50, 47),
    "blue": (38, 139, 210),
    "green": (133, 153, 0),
    "purple": (108, 113, 196),
    "orange": (203, 75, 22),
    "cyan": (42, 161, 152),
    "pink": (211, 54, 130),
    "brown": (131, 99, 76),
}

CONTROL_LABELS = {
    "manual": "Human",
    "random": "Random",
    "agent": "Agent",
}


class PlayerPanel(UIElement):
    def __init__(
        self,
        rect: pg.Rect,
        players,
        #Avoid direct access to the game model from the UI. Instead, use a callback to get the current player.
        get_current_player: Callable[[], int],
        on_control_change: Callable[[int], None],
        on_load_agent: Callable[[int], None],
    ):
        super().__init__(rect)

        self.players = players

        self.on_control_change = on_control_change
        self.on_load_agent = on_load_agent
        self.get_current_player = get_current_player

        self.replay_mode = False

        self.color_cells: dict[tuple[int, str], pg.Rect] = {}
        self.control_buttons: dict[int, pg.Rect] = {}
        self.load_agent_buttons: dict[int, pg.Rect] = {}

        self.font = ft.SysFont(None, 22)
    
    #--------------------------------------------------
    # Event handling
    #--------------------------------------------------
    
    def handle_event(self, ev: pg.event.Event) -> None:
        if self.replay_mode:
            return

        if ev.type != pg.MOUSEBUTTONDOWN or ev.button != 1:
            return

        # Color selection
        for (player_id, color_name), rect in self.color_cells.items():
            if rect.collidepoint(ev.pos):
                self._change_color(player_id, color_name)
                return

        # Control selection
        for player_id, rect in self.control_buttons.items():
            if rect.collidepoint(ev.pos):
                self.on_control_change(player_id)
                return

        # Agent loading / unloading
        for player_id, rect in self.load_agent_buttons.items():
            if rect.collidepoint(ev.pos):
                self.on_load_agent(player_id)
                return

    #--------------------------------------------------
    # Rendering
    #--------------------------------------------------

    def render(self, surf: pg.Surface) -> None:
        pg.draw.rect(surf, (50, 50, 50), self.rect)

        self.color_cells.clear()
        self.control_buttons.clear()
        self.load_agent_buttons.clear()

        card_h = self.rect.height // 4

        for player_id in range(1, 5):
            player = self.players[player_id]

            card = pg.Rect(
                self.rect.x + 10,
                self.rect.y + (player_id - 1) * card_h,
                self.rect.width - 20,
                card_h - 10,
            )

            pg.draw.rect(
                surf,
                (60, 60, 60),
                card,
                border_radius=6,
            )

            if player_id == self.get_current_player():
                pg.draw.rect(
                    surf,
                    (200, 200, 200),
                    card,
                    width=2,
                    border_radius=6,
                )

            self._render_header(surf, card, player)
            self._render_buttons(surf, card, player)
            self._render_colors(surf, card, player)
            
            
    #--------------------------------------------------
    # Private helper methods
    #--------------------------------------------------
    
    def _change_color(self, player_id: int, color_name: str) -> None:
        player = self.players[player_id]

        # Check whether another player already owns this color.
        for other in self.players.values():
            if other.Which_Player != player_id and other.Color == color_name:
                return

        player.Color = color_name

    def _format_time(self, milliseconds: int) -> str:
        total_seconds = max(0, milliseconds // 1000)
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def _render_header(self, surf, card, player) -> None:
        self.font.render_to(
            surf,
            (card.x + 10, card.y + 8),
            f"PLAYER {player.Which_Player}",
            fgcolor=COLORS[player.Color],
        )

        clock_text = self._format_time(player.time_ms)

        clock_color = (
            (220, 50, 47)
            if player.time_ms < 30_000
            else (230, 230, 230)
        )

        self.font.render_to(
            surf,
            (card.right - 70, card.y + 8),
            clock_text,
            fgcolor=clock_color,
        )

    def _render_buttons(self, surf, card, player) -> None:
        player_id = player.Which_Player

        btn_w = 100
        btn_h = 26

        ctrl_rect = pg.Rect(
            card.x + 10,
            card.y + 40,
            btn_w,
            btn_h,
        )

        load_rect = pg.Rect(
            ctrl_rect.right + 10,
            ctrl_rect.y,
            btn_w,
            btn_h,
        )

        control_label = (
            "Replay"
            if self.replay_mode
            else CONTROL_LABELS.get(player.Control, player.Control or "Human")
        )

        load_label = (
            "Unload"
            if player.agent is not None and not self.replay_mode
            else "Load"
        )

        ctrl_color = (65, 65, 65) if self.replay_mode else (80, 80, 80)
        load_color = (50, 65, 50) if self.replay_mode else (60, 90, 60)

        pg.draw.rect(
            surf, ctrl_color, ctrl_rect, border_radius=4
        )
        pg.draw.rect(
            surf, load_color, load_rect, border_radius=4
        )

        self.font.render_to(
            surf,
            (ctrl_rect.x + 6, ctrl_rect.y + 5),
            control_label,
            fgcolor=(230, 230, 230),
        )

        self.font.render_to(
            surf,
            (load_rect.x + 6, load_rect.y + 5),
            load_label,
            fgcolor=(230, 230, 230),
        )

        self.control_buttons[player_id] = ctrl_rect
        self.load_agent_buttons[player_id] = load_rect

    def _render_colors(self, surf, card, player) -> None:
        cell_size = self.rect.height // 20
        gap = 6

        start_x = card.x + 10
        start_y = card.bottom - (cell_size * 2 + gap + 10)

        occupied = {
            other.Color
            for other in self.players.values()
            if other.Which_Player != player.Which_Player
        }

        for index, (color_name, rgb) in enumerate(COLORS.items()):
            row = index // 4
            col = index % 4

            rect = pg.Rect(
                start_x + col * (cell_size + gap),
                start_y + row * (cell_size + gap),
                cell_size,
                cell_size,
            )

            pg.draw.rect(surf, rgb, rect)

            if player.Color == color_name:
                pg.draw.rect(
                    surf, (255, 255, 255), rect, width=3
                )
            elif color_name in occupied:
                pg.draw.rect(
                    surf, (0, 0, 0), rect, width=2
                )

            self.color_cells[
                (player.Which_Player, color_name)
            ] = rect