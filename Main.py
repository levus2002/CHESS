import pygame as pg
from pygame import freetype
import sys
import pygame.freetype as ft
from enum import Enum

from Persistence.Board import Board
from Persistence.Player import Player
from Persistence.Type import Type

#------------------------------------------------------------------------------------+
#| Menüsor                         |                                                 |
#|New Game | Save Game |  Load Game|                                                 |
#----------------------+-------------------------------------------------------------|
#                      |                                                             |
# Player1      TIME    |                    [B][H][F][K][V][F][H][B]                 |
# COLOR:               |                    [G][G][G][G][G][G][G][G]                 |
# [][][][]             |                    [ ][#][ ][#][ ][#][ ][#]                 |
# [][][][]             |           [B][G][ ][#][ ][#][ ][#][ ][#][ ][#][G][B]        |
# Player2      TIME    |           [H][G][#][ ][#][ ][#][ ][#][ ][#][ ][G][H]        |
# COLOR:               |           [F][G][ ][#][ ][#][ ][#][ ][#][ ][#][G][F]        |
# [][][][]             |           [K][G][#][ ][#][ ][#][ ][#][ ][#][ ][G][V]        |
# [][][][]             |           [V][G][ ][#][ ][#][ ][#][ ][#][ ][#][G][K]        |
# Player3      TIME    |           [F][G][#][ ][#][ ][#][ ][#][ ][#][ ][G][F]        |
# COLOR:               |           [H][G][ ][#][ ][#][ ][#][ ][#][ ][#][G][H]        |
# [][][][]             |           [B][G][#][ ][#][ ][#][ ][#][ ][#][ ][G][B]        |
# [][][][]             |                    [#][ ][#][ ][#][ ][#][ ]                 |
# Player4      TIME    |                    [G][G][G][G][G][G][G][G]                 |
# COLOR:               |                    [B][H][F][V][K][F][H][B]                 |
# [][][][]             |                                                             |
# [][][][]             |                                                             |
#----------------------+-------------------------------------------------------------+
#Státuszsor  lépés, idő ilyesmi                                                      |
#------------------------------------------------------------------------------------+

# ---------- Konfiguráció ----------
WINDOW_W, WINDOW_H = 1200, 720
FPS = 20

# relatív elrendezés
LEFT_PANEL_RATIO = 0.25  # menü / player panel szélessége az ablakhoz képest
RIGHT_PANEL_RATIO = 1.0 - LEFT_PANEL_RATIO

# board méret
BOARD_ROWS = 14
BOARD_COLS = 14


UNICODE_PIECES = {
    "K": "♚", "Q": "♛", "R": "♜", "B": "♝", "N": "♞", "P": "♟",
    # világos változat ♔ ♕ ♖ ♗ ♘ ♙
    # sötét változat : ♚ ♛ ♜ ♝ ♞ ♟
}
COLORS = {
    "red": {"player": 1, "rgb": (220, 50, 47)},
    "blue": {"player": 2, "rgb": (38, 139, 210)},
    "green": {"player": 3, "rgb": (133, 153, 0)},
    "purple": {"player": 4, "rgb": (108, 113, 196)},
    "orange": {"player": None, "rgb": (203, 75, 22)},
    "teal": {"player": None, "rgb": (42, 161, 152)},
    "magenta": {"player": None, "rgb": (211, 54, 130)},
    "brown": {"player": None, "rgb": (133, 94, 66)}
}

PLAYER_COLORS = {
    1: "red" ,
    2: "blue", 
    3: "green",   
    4: "purple",
}
SQUARE_LIGHT = (220, 220, 220)   # világos szürke
SQUARE_DARK = (170, 170, 170)    # sötétebb szürke

TARGET_BORDER = {
    0: None,
    1: (0, 120, 0),     # selected: sötét zöld
    2: (144, 238, 144), # move: világos zöld
    3: (200, 40, 40),   # capture: piros
}
player_corners = {
    (0,13):1,
    (13,13):2,
    (13,0):3,
    (0,0):4
}
# -1 nem a tábla része
# 0 világos mező
# 1 sötét mező
board_fields = [
    [-1, -1, -1, 1, 0, 1, 0, 1, 0, 1, 0, -1, -1, -1],
    [-1, -1, -1, 0, 1, 0, 1, 0, 1, 0, 1, -1, -1, -1],
    [-1, -1, -1, 1, 0, 1, 0, 1, 0, 1, 0, -1, -1, -1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],
    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
    [-1, -1, -1, 0, 1, 0, 1, 0, 1, 0, 1, -1, -1, -1],
    [-1, -1, -1, 1, 0, 1, 0, 1, 0, 1, 0, -1, -1, -1],
    [-1, -1, -1, 0, 1, 0, 1, 0, 1, 0, 1, -1, -1, -1]]


    


    
def format_time(ms):
    total_sec = ms // 1000
    minutes = total_sec // 60
    seconds = total_sec % 60
    return f"{minutes:02}:{seconds:02}"
    

class UIElement:
    def __init__(self, rect: pg.Rect):
        self.rect = rect
    def handle_event(self, ev, app): ...
    def render(self, surf, app): ...
class MenuBar(UIElement):
    def __init__(self, rect: pg.Rect, buttons: list[str]):
        super().__init__(rect)
        self.buttons = buttons
        self.button_rects = {}

    def handle_event(self, ev, app):
        if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
            for text, rect in self.button_rects.items():
                if rect.collidepoint(ev.pos):
                    if text == "New Game":
                        app.newgame()
                    elif text == "Save Game":
                        print("Save Game clicked")
                    elif text == "Load Game":
                        print("Load Game clicked")
                    return

    def render(self, surf, app):
        self.button_rects.clear()
        font = ft.SysFont(None, 18)
        gap = 8
        x = self.rect.x + 10
        y = self.rect.y + 10
        btn_h = 28

        for text in self.buttons:
            btn_w = font.get_rect(text).width + 16
            rect = pg.Rect(x, y, btn_w, btn_h)
            pg.draw.rect(surf, (70,70,70), rect, border_radius=4)
            font.render_to(surf, (x + 8, y + 6), text, fgcolor=(230,230,230))
            self.button_rects[text] = rect
            x += btn_w + gap
            
class LeftPanel(UIElement):
    def __init__(self, rect: pg.Rect):
        super().__init__(rect)
        self.color_cells = {}

    def handle_event(self, ev, app):
        if ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
            for (player_id, color_name), rect in self.color_cells.items():
                if rect.collidepoint(ev.pos):
                    player = app.board.get_player(player_id)
                    owner = COLORS[color_name]["player"]

                    if owner is None or owner == player.Which_Player:
                        if player.Color != color_name:
                            # Free old color
                            COLORS[player.Color]["player"] = None

                            # Assign new color
                            COLORS[color_name]["player"] = player.Which_Player
                            player.Color = color_name
                    break

    def render(self, surf, app):
        # Background
        pg.draw.rect(surf, (40,40,40), self.rect)


        card_h = self.rect.height // 4
        font = ft.SysFont(None, 22)
        self.color_cells.clear()

        for i in range(1,5):
            player=app.board.get_player(i)
            r = pg.Rect(
                self.rect.x + 10,
                self.rect.y + (i-1) * card_h,
                self.rect.width - 20,
                card_h - 10
            )
            pg.draw.rect(surf, (60,60,60), r, border_radius=6)

            # Highlight current player
            if player == app.board.get_current_player():
                pg.draw.rect(surf, (200,200,200), r, width=2)

            # PLAYER NAME
            font.render_to(
                surf,
                (r.x + 10, r.y + 8),
                f"PLAYER {player.Which_Player}",
                #fgcolor=(230,230,230)
                fgcolor=COLORS[player.Color]["rgb"]
            )

            # CLOCK
            clock_text = format_time(player.time_ms)
            time_color = (220,50,47) if player.time_ms < 30000 else (230,230,230)
            font.render_to(
                surf,
                (r.right - 70, r.y + 8),
                clock_text,
                fgcolor=time_color
            )

            # Color grid
            cell_size = self.rect.height//20
            gap = 6
            start_x = r.x + 10
            start_y = r.bottom - (cell_size*2 + gap + 10)

            color_names = list(COLORS.keys())
            for j, cname in enumerate(color_names):
                row = j // 4
                col = j % 4
                cx = start_x + col * (cell_size + gap)
                cy = start_y + row * (cell_size + gap)
                cell_rect = pg.Rect(cx, cy, cell_size, cell_size)

                # draw color
                pg.draw.rect(surf, COLORS[cname]["rgb"], cell_rect)

                # owned color
                if player.Color == cname:
                    pg.draw.rect(surf, (255,255,255), cell_rect, width=3)
                # Taken color
                elif COLORS[cname]["player"] is not None:
                    pg.draw.rect(surf, (0,0,0), cell_rect, width=2)

                # save rect for click handling
                self.color_cells[(player.Which_Player, cname)] = cell_rect

                
class BoardField(UIElement):

    def __init__(self, rect: pg.Rect, rows, cols, board):
        super().__init__(rect)
        self.rows = rows; self.cols = cols
        self.board=board
        self.selected = None
        self.padding_px = 8

    def compute_layout(self):
        # padding dinamikusan: kis százalék, de legalább 8px
        pad = max(8, int(min(self.rect.width, self.rect.height) * 0.02))
        side = min(self.rect.width, self.rect.height) - 2*pad
        if side <= 0:
            side = min(self.rect.width, self.rect.height)
            pad = 0
        cell_size = side / self.cols
        board_px = self.rect.x + (self.rect.width - side) / 2
        board_py = self.rect.y + (self.rect.height - side) / 2
        return pad, side, cell_size, board_px, board_py

    def handle_event(self, ev, app):
        current=self.board.current_player_index
        if ev.type==pg.MOUSEBUTTONDOWN and ev.button==1 and self.rect.collidepoint(ev.pos) and not self.board.is_game_over:
            mx,my = ev.pos
            pad, side, cell_size, board_px, board_py = self.compute_layout()
            rel_x = mx - board_px; rel_y = my - board_py
            col = int(rel_x // cell_size); row = int(rel_y // cell_size)
            if 0 <= row < self.rows and 0 <= col < self.cols and board_fields[row][col] != -1:
                entry = self.board.board_state[row][col]
                print(entry)
                if self.board.selected_figure is None:
                    if entry == current:
                        self.selected = (row, col)
                        self.board.select_figure(row, col)
                else:
                    moved = self.board.try_move(row, col)
                    if moved:
                        self.selected = None
                    else:
                        if entry == current:
                            self.selected = (row, col)
                            self.board.select_figure(row, col)
                        else:
                            self.selected = None
                            self.board.board_targets = self.board.empty_board()      

                print("Board clicked cell:", (row,col))
            else:
                self.selected = None
                self.board.board_targets = self.board.empty_board()
                print("Click outside playable board or on OOB cell.")
    
    def render(self, surf, app):
        pad, side, cell_size, board_px, board_py = self.compute_layout()
        # board background
        pg.draw.rect(surf, (60,60,60), self.rect)
        # squares
        for r in range(self.rows):
            for c in range(self.cols):
                bf = board_fields[r][c]                    
                sx = int(board_px + c*cell_size)
                sy = int(board_py + r*cell_size)
                rect = pg.Rect(sx, sy, int(cell_size)+1, int(cell_size)+1)
                color = SQUARE_DARK if bf == 1 else SQUARE_LIGHT
                if (r,c) in player_corners:
                    pg.draw.rect(surf, SQUARE_LIGHT, rect)

                    p = self.board.get_player(player_corners[(r,c)])
                    rcol = COLORS[p.Color]["rgb"]

                    text = f"{p.Reward:+.2f}"
                    font_sz = int(cell_size * 0.3)
                    piece_font = ft.SysFont("Segoe UI Symbol", font_sz)

                    text_rect = piece_font.get_rect(text)
                    text_rect.center = rect.center

                    piece_font.render_to(surf, text_rect, text, rcol)
                if bf == -1:
                    continue
                pg.draw.rect(surf, color, rect)
                # selection/target highlight
                match self.board.board_targets[r][c]:
                    case 1:
                        pg.draw.rect(surf, TARGET_BORDER[1], rect, width=4)
                    case 2:
                        pg.draw.rect(surf, TARGET_BORDER[2], rect, width=4)
                    case 3:
                        pg.draw.rect(surf, TARGET_BORDER[3], rect, width=4)
                    case 4:
                        pg.draw.rect(surf, COLORS["blue"]["rgb"], rect, width=4)
                # piece render from piece_grid
                entry = self.board.board_state[r][c]
                if entry <=0:
                    continue
                player=self.board.get_player(entry)
                Fig=player.get_figure(r,c)
                ch = UNICODE_PIECES[Fig.Type.char]
                font_sz = max(12, int(cell_size * 0.8))
                piece_font = ft.SysFont("Segoe UI Symbol", font_sz)
                bbox = piece_font.get_rect(ch)
                px = int(board_px + c*cell_size + cell_size/2 - bbox.width//2)
                py = int(board_py + r*cell_size + cell_size/2 - bbox.height//2)
                fg = COLORS[self.board.get_player(entry).Color]["rgb"]
                piece_font.render_to(surf, (px, py), ch, fgcolor=fg)   
            
                



class StatusBar(UIElement):
    def __init__(self, rect: pg.Rect):
        super().__init__(rect)
        self.message = ""

    def render(self, surf, app):
        pg.draw.rect(surf, (50,50,50), self.rect)

        font = ft.SysFont(None, 18)

        player = app.board.get_current_player()
        player_color = player.Color
        move = app.board.move_number if hasattr(app.board, "move_number") else "?"

        text = f"Turn: Player {player.Which_Player} ({player_color}) | Move: {move}"

        font.render_to(
            surf,
            (self.rect.x + 8, self.rect.y + 10),
            text,
            fgcolor=(230,230,230)
        )

        if self.message:
            font.render_to(
                surf,
                (self.rect.right//2, self.rect.y + 10),
                self.message,
                fgcolor=(230,230,230)
            )
            
# ---------- App (init + loop) ----------
class App:
    def __init__(self):
        pg.init()
        pg.display.set_caption("4-player chess")
        self.screen = pg.display.set_mode((WINDOW_W, WINDOW_H), pg.RESIZABLE)
        self.clock = pg.time.Clock()
        self.status_timer = 2000
        self.player1=Player(1,"red")
        self.player2=Player(2,"blue")
        self.player3=Player(3,"green")
        self.player4=Player(4,"purple")
        self.board=Board(self.player1, self.player2, self.player3, self.player4)
        self.newgame()
        # UI elements lesznek frameenként újraszámolva rect alapján
        # board wrapper (tárolja a piece_grid és board_fields)
        self.board_panel = BoardField(pg.Rect(0,0,100,100), BOARD_ROWS, BOARD_COLS, self.board)
        self.left_panel = LeftPanel(pg.Rect(0,0,100,100))
        self.menu_bar = MenuBar(
        pg.Rect(0, 0, int(WINDOW_W*LEFT_PANEL_RATIO), 50),
        ["New Game", "Save Game", "Load Game"]
    )
        self.status = StatusBar(pg.Rect(0,0,100,20))

    def layout(self):
        w,h = self.screen.get_size()
        left_w = int(w * LEFT_PANEL_RATIO)
        menu_h=50
        bottom_h = 40
        left_rect = pg.Rect(0, menu_h, left_w, h - bottom_h-menu_h)
        board_rect = pg.Rect(left_w, menu_h, w - left_w, h - bottom_h-menu_h)
        status_rect = pg.Rect(0, h - bottom_h, w, bottom_h)
        self.left_panel.rect = left_rect
        self.board_panel.rect = board_rect
        self.status.rect = status_rect

    def handle_events(self):
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                return False
            if ev.type == pg.VIDEORESIZE:
                self.screen = pg.display.set_mode((ev.w, ev.h), pg.RESIZABLE)
            # propagate to UI elements (order: left panel, board, status)
            self.left_panel.handle_event(ev, self)
            self.board_panel.handle_event(ev, self)
            self.menu_bar.handle_event(ev, self)
            self.status.handle_event(ev, self)
        return True

    def update(self, dt):
        self.status.message=self.board.msg
        

        if not self.board.is_game_over:
            if self.status_timer > 0 and self.status.message != "":
                self.status_timer -= dt
            else:
                self.board.msg = ""
                self.status_timer = 2000
            
            player = self.board.get_current_player()
            player.time_ms = max(0, player.time_ms - dt)
            if player.time_ms==0:
                player.IsDefeated=True
                self.status.message = f"PLAYER {player.Which_Player} is Defeated"
        

    def render(self):
        self.screen.fill((30,30,30))
        # render elemek
        self.menu_bar.render(self.screen, self)
        self.left_panel.render(self.screen, self)
        self.board_panel.render(self.screen, self)
        self.status.render(self.screen, self)
        pg.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            self.layout()
            running = self.handle_events()
            self.update(dt)
            self.render()
        pg.quit()
        sys.exit()

    def newgame(self):
        self.board.newgame()












































def main():
    App().run()

if __name__ == "__main__":
    main()
    
    
