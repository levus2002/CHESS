import pygame as pg
from pygame import freetype
import sys
import pygame.freetype as ft

from Persistence.Board import Board
from Persistence.Player import Player
from Persistence.Type import Type

#------------------------------------------------------------------------------------+
#| Menüsor                         |                                                 |
#|New Game | Save Game |  Load Game|                                                 |
#----------------------+-------------------------------------------------------------|
#                      |                                                             |
# Player1 Username:    |                    [B][H][F][K][V][F][H][B]                 |
# _________            |                    [G][G][G][G][G][G][G][G]                 |
# Color:[]             |                    [ ][#][ ][#][ ][#][ ][#]                 |
#                      |           [B][G][ ][#][ ][#][ ][#][ ][#][ ][#][G][B]        |
# Player2 Username:    |           [H][G][#][ ][#][ ][#][ ][#][ ][#][ ][G][H]        |
# _________            |           [F][G][ ][#][ ][#][ ][#][ ][#][ ][#][G][F]        |
# Color:[]             |           [K][G][#][ ][#][ ][#][ ][#][ ][#][ ][G][V]        |
#                      |           [V][G][ ][#][ ][#][ ][#][ ][#][ ][#][G][K]        |
# Player2 Username:    |           [F][G][#][ ][#][ ][#][ ][#][ ][#][ ][G][F]        |
# _________            |           [H][G][ ][#][ ][#][ ][#][ ][#][ ][#][G][H]        |
# Color:[]             |           [B][G][#][ ][#][ ][#][ ][#][ ][#][ ][G][B]        |
#                      |                    [#][ ][#][ ][#][ ][#][ ]                 |
# Player2 Username:    |                    [G][G][G][G][G][G][G][G]                 |
# _________            |                    [B][H][F][V][K][F][H][B]                 |
# Color:[]             |                                                             |
#                      |                                                             |
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
PLAYER_COLORS = {
    1: (200, 40, 40),   # piros / player1
    2: (40, 80, 200),   # kék / player2
    3: (40, 140, 40),   # sötét zöld / player3
    4: (120, 40, 140),  # lila / player4
}
SQUARE_LIGHT = (220, 220, 220)   # világos szürke
SQUARE_DARK = (170, 170, 170)    # sötétebb szürke

TARGET_BORDER = {
    0: None,
    1: (0, 120, 0),     # selected: sötét zöld
    2: (144, 238, 144), # move: világos zöld
    3: (200, 40, 40),   # capture: piros
}
#
# Nem szeretném megjelenítés közben számolni, hogy mező milyen színű illetve, hogy a tábla része-e
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


# Új játékot indítunk
def newgame():
    player1=Player(1, PLAYER_COLORS[1])
    player2=Player(2, PLAYER_COLORS[2])
    player3=Player(3, PLAYER_COLORS[3])
    player4=Player(4, PLAYER_COLORS[4])
    board=Board(player1, player2, player3, player4)
    


    

    

class UIElement:
    def __init__(self, rect: pg.Rect):
        self.rect = rect
    def handle_event(self, ev, app): ...
    def render(self, surf, app): ...

class LeftPanel(UIElement):
    def __init__(self, rect: pg.Rect):
        super().__init__(rect)
    def render(self, surf, app):
        pg.draw.rect(surf, (40,40,40), self.rect)
        btn_h, gap = 30, 8
        btn_w = max(10, self.rect.width - 20)
        for i, txt in enumerate(["New Game","Save Game","Load Game"]):
            r = pg.Rect(self.rect.x+10, self.rect.y+10 + i*(btn_h+gap), btn_w, btn_h)
            pg.draw.rect(surf, (70,70,70), r, border_radius=4)
            ft.SysFont(None, 18).render_to(surf, (r.x+8, r.y+6), txt, fgcolor=(230,230,230))
    def handle_event(self, ev, app):
        if ev.type==pg.MOUSEBUTTONDOWN and ev.button==1 and self.rect.collidepoint(ev.pos):
            print("Left panel clicked")

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
                match self.board.board_targets[row][col]:
                    case 0:
                        # Ha a kattintott figura a soron következő játékosé
                        if entry == current :
                            Fig = self.board.get_player(current).get_figure(row, col)# type: ignore
                            if Fig is not None:
                                self.selected = (row, col)
                                self.board.board_targets = self.board.get_moves(Fig)
                    case 1:
                        self.selected = None
                        self.board.board_targets = self.board.empty_board()
                    case 2:
                        r,c=self.selected # type: ignore
                        self.board.make_move(r,c,row,col)
                        self.selected = None
                        self.board.board_targets = self.board.empty_board()
                        #make_move(r,c,row,col,self.board)
                    case 3:
                        r,c=self.selected # type: ignore
                        self.board.make_move(r,c,row,col)
                        self.selected = None
                        self.board.board_targets = self.board.empty_board()
                        #make_move(r,c,row,col,self.board)

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
                if bf == -1:
                    continue
                sx = int(board_px + c*cell_size)
                sy = int(board_py + r*cell_size)
                rect = pg.Rect(sx, sy, int(cell_size)+1, int(cell_size)+1)
                color = SQUARE_DARK if bf == 1 else SQUARE_LIGHT
                pg.draw.rect(surf, color, rect)
                # selection/target highlight
                match self.board.board_targets[r][c]:
                    case 1:
                        pg.draw.rect(surf, TARGET_BORDER[1], rect, width=4)
                    case 2:
                        pg.draw.rect(surf, TARGET_BORDER[2], rect, width=4)
                    case 3:
                        pg.draw.rect(surf, TARGET_BORDER[3], rect, width=4)
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
                fg = player.Color 
                piece_font.render_to(surf, (px, py), ch, fgcolor=fg)   
            
                



class StatusBar(UIElement):
    def __init__(self, rect: pg.Rect):
        super().__init__(rect)
    def render(self, surf, app):
        pg.draw.rect(surf, (50,50,50), self.rect)
        #ft.SysFont(None, 18).render_to(surf, (self.rect.x+8, self.rect.y+6), fgcolor=(230,230,230))

# ---------- App (init + loop) ----------
class App:
    def __init__(self):
        pg.init()
        pg.display.set_caption("4-player chess - refactor demo")
        self.screen = pg.display.set_mode((WINDOW_W, WINDOW_H), pg.RESIZABLE)
        self.clock = pg.time.Clock()
        
        self.player1=Player(1, PLAYER_COLORS[1])
        self.player2=Player(2, PLAYER_COLORS[2])
        self.player3=Player(3, PLAYER_COLORS[3])
        self.player4=Player(4, PLAYER_COLORS[4])
        self.board=Board(self.player1, self.player2, self.player3, self.player4)
        # UI elements lesznek frameenként újraszámolva rect alapján
        # board wrapper (tárolja a piece_grid és board_fields)
        self.board_panel = BoardField(pg.Rect(0,0,100,100), BOARD_ROWS, BOARD_COLS, self.board)
        # placeholder left panel, status bar recteket a layout() állítja be
        self.left_panel = LeftPanel(pg.Rect(0,0,100,100))
        self.status = StatusBar(pg.Rect(0,0,100,20))

    def layout(self):
        w,h = self.screen.get_size()
        left_w = int(w * LEFT_PANEL_RATIO)
        bottom_h = 40
        left_rect = pg.Rect(0, 0, left_w, h - bottom_h)
        board_rect = pg.Rect(left_w, 0, w - left_w, h - bottom_h)
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
            self.status.handle_event(ev, self)
        return True

    def update(self, dt):
        pass

    def render(self):
        self.screen.fill((30,30,30))
        # render elemek
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

def main():
    App().run()

if __name__ == "__main__":
    main()
    
    
