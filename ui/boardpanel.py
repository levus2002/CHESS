
import pygame as pg
import pygame.freetype as ft

from ui.base import UIElement
from Model.GameModel import GameModel


BOARD_SIZE = 14

SQUARE_LIGHT = (225, 226, 228)
SQUARE_DARK = (166, 168, 170)

TARGET_COLORS = {
    1: (70, 190, 90),     # Ordinary move
    2: (220, 65, 65),     # Capture
    3: (235, 190, 55),    # Promotion
}

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

UNICODE_PIECES = {
    "P": "♟",
    "N": "♞",
    "B": "♝",
    "R": "♜",
    "Q": "♛",
    "K": "♚",
}

PROMOTIONS = ("N", "B", "R", "Q")


class BoardPanel(UIElement):
    def __init__(self, rect: pg.Rect, game_model: GameModel):
        super().__init__(rect)

        self.game_model = game_model

        self.replay_mode = False
        self.highlights = [[0] * 14 for _ in range(14)]
        # During promotion.
        self.pending_actions = []

        self.board_rect = pg.Rect(0, 0, 0, 0)
        self.cell_size = 0

        self.promotion_rects: dict[str, pg.Rect] = {}

        # Font cache, to avoid recreation.
        self.fonts: dict[int, ft.Font] = {}

    # --------------------------------------------------
    # Layout
    # --------------------------------------------------

    def compute_layout(self) -> None:
        # Leave room at the top for promotion choices.
        padding = 8
        top_space = 55

        available_width = max(0, self.rect.width - padding * 2)
        available_height = max(0, self.rect.height - top_space - padding)

        side = min(available_width, available_height)
        self.cell_size = side // BOARD_SIZE

        board_side = self.cell_size * BOARD_SIZE

        self.board_rect = pg.Rect(
            self.rect.x + (self.rect.width - board_side) // 2,
            self.rect.y + top_space,
            board_side,
            board_side,
        )
    # --------------------------------------------------
    # Events
    # --------------------------------------------------

    def handle_event(self, ev: pg.event.Event) -> None:
        if self.replay_mode or self.game_model.isgameover:
            return

        if self.game_model.CurrentPlayer().Control != "manual":
            return

        if ev.type != pg.MOUSEBUTTONDOWN or ev.button != 1:
            return

        self.compute_layout()

        # Promotion choices take priority over board clicks.
        if self.pending_actions:
            self._handle_promotion_click(ev.pos)
            return

        cell = self._mouse_to_cell(ev.pos)

        if cell is None:
            self._clear_selection()
            return

        self._handle_board_click(*cell)

    def _handle_board_click(self, row: int, col: int) -> None:
        game = self.game_model

        actions = game.action_lookup.get((row, col), [])

        if actions:
            if len(actions) == 1:
                game.step(actions[0])
                self._clear_selection()

            else:
                # Promotion creates multiple action instances, one for each figure it can promote into.
                self.pending_actions = actions

            return

        figure = game.board.get_figure(row, col)

        if (
            figure is not None
            and figure.Player == game.current_player
        ):
            self.highlights = game.select_figure(row, col)
            return

        self._clear_selection()

    def _handle_promotion_click(self, pos) -> None:
        for promotion, rect in self.promotion_rects.items():
            if not rect.collidepoint(pos):
                continue

            action = next(
                (
                    action
                    for action in self.pending_actions
                    if action.promotion == promotion
                ),
                None,
            )

            if action is not None:
                self.game_model.step(action)

            self._clear_selection()
            return

        # Clicking outside the promotion menu cancels the choice.
        self.pending_actions.clear()

    def _clear_selection(self) -> None:
        self.pending_actions.clear()
        self.promotion_rects.clear()
        self.highlights = [[0] * 14 for _ in range(14)]

        self.game_model.clear_selection()

    # --------------------------------------------------
    # Rendering
    # --------------------------------------------------

    def render(self, surf: pg.Surface) -> None:
        self.compute_layout()

        pg.draw.rect(surf, (50, 50, 50), self.rect)

        if self.cell_size <= 0:
            return

        self.render_tiles(surf)
        self.render_targets(surf)
        self.render_figures(surf)

        if self.pending_actions:
            self.render_promotion_menu(surf)

    def render_tiles(self, surf: pg.Surface) -> None:
        board = self.game_model.board

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if not board.in_bounds(row, col):
                    continue

                rect = self._cell_rect(row, col)

                color = (
                    SQUARE_LIGHT
                    if (row + col) % 2 == 0
                    else SQUARE_DARK
                )

                pg.draw.rect(surf, color, rect)

    def render_targets(self, surf: pg.Surface) -> None:
        for row in range(14):
            for col in range(14):
                target = self.highlights[row][col]

                if target == 0:
                    continue

                pg.draw.rect(
                    surf,
                    TARGET_COLORS[target],
                    self._cell_rect(row, col),
                    width=max(2, self.cell_size // 12),
                )

        selected = self.game_model.selected_figure

        if selected is not None:
            pg.draw.rect(
                surf,
                (65, 130, 230),
                self._cell_rect(selected.X, selected.Y),
                width=max(2, self.cell_size // 12),
            )

    def render_figures(self, surf: pg.Surface) -> None:
        board = self.game_model.board

        font = self._get_font(int(self.cell_size * 0.8))

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if not board.in_bounds(row, col):
                    continue
                figure = board.get_figure(row, col)

                if figure is None:
                    continue

                player = self.game_model.get_player(figure.Player)

                symbol = UNICODE_PIECES[figure.Type.char]
                color = COLORS[player.Color] # type: ignore

                # Defeated players pieces remain and get greyed out.
                if player.IsDefeated:
                    color = (110, 110, 110)

                cell = self._cell_rect(row, col)

                text_rect = font.get_rect(symbol)
                text_rect.center = cell.center

                font.render_to(
                    surf,
                    text_rect,
                    symbol,
                    fgcolor=color,
                )

    def render_promotion_menu(self, surf: pg.Surface) -> None:
        self.promotion_rects.clear()

        player = self.game_model.CurrentPlayer()
        color = COLORS[player.Color] # type: ignore

        font = self._get_font(int(self.cell_size * 0.8))

        menu_width = self.cell_size * 4
        start_x = self.board_rect.centerx - menu_width // 2
        start_y = self.board_rect.y - self.cell_size - 6

        for index, promotion in enumerate(PROMOTIONS):
            rect = pg.Rect(
                start_x + index * self.cell_size,
                start_y,
                self.cell_size,
                self.cell_size,
            )

            pg.draw.rect(surf, (210, 210, 210), rect)
            pg.draw.rect(surf, (80, 80, 80), rect, width=1)

            symbol = UNICODE_PIECES[promotion]

            text_rect = font.get_rect(symbol)
            text_rect.center = rect.center

            font.render_to(
                surf,
                text_rect,
                symbol,
                fgcolor=color,
            )

            self.promotion_rects[promotion] = rect







    #--------------------------------------------------
    # Private helper methods
    #-------------------------------------------------
    
    def _cell_rect(self, row: int, col: int) -> pg.Rect:
        return pg.Rect(
            self.board_rect.x + col * self.cell_size,
            self.board_rect.y + row * self.cell_size,
            self.cell_size,
            self.cell_size,
        )

    def _mouse_to_cell(self, pos) -> tuple[int, int] | None:
        if self.cell_size <= 0:
            return None

        if not self.board_rect.collidepoint(pos):
            return None

        col = (pos[0] - self.board_rect.x) // self.cell_size
        row = (pos[1] - self.board_rect.y) // self.cell_size

        if not self.game_model.board.in_bounds(row, col):
            return None

        return row, col

    def _get_font(self, size: int) -> ft.Font:
        size = max(12, size)

        if size not in self.fonts:
            self.fonts[size] = ft.SysFont("Segoe UI Symbol", size)

        return self.fonts[size]
        
    