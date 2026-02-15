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
FPS = 60

# relatív elrendezés
LEFT_PANEL_RATIO = 0.25  # menü / player panel szélessége az ablakhoz képest
RIGHT_PANEL_RATIO = 1.0 - LEFT_PANEL_RATIO

# board méret
BOARD_ROWS = 14
BOARD_COLS = 14





    
    
    
# Pygame megjelenítés minden frameben újrarajzolja a játékteret, nem akarom minden frameben kiszámolni, 
# hogy a kiválasztott bábu melyik mezőkre tud lépni illetve ütni
# -1 nem a tábla része
# 0 nem érintett mező nincs keret/fekete keret 
# 1 kiválasztott bábu itt áll mező sötét zöld keret
# 2 kiválasztott bábu ide tud lépni, világosabb zöld keret
# 3 kiválasztott bábu az itt álló bábu ütni tudja piros keret
board_targets = [
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1]]

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

Current_Player=1


    
# click event
# Ablak átméretezés kedvéért relatív méretet használok.
#x<0.1 menüsör nézzük meg a menügombokat, hogy meglettek-e enyomva
#x>0.9 státuszsor nincs interakció
#egyébb akkor a click a játékteret érintette, nézzük meg melyik mező lett megnyomva, ha mező volt.


#Board osztály és player osztályok létrehozása és setupolása
#def setup_game():

    
# Ha a click egy valid mezőt érintett
# Boardtól megkérdezzük mi a mező fieldstateje, vagyis áll e ott figura és melyik játékosé
# Ha van már selected bábu, és erre a mezőre tudunk lépni akkor lépjünk oda
# Ha van selected és nem tudunk ide lépni, mert itt is a mi bábunk áll, akkor legyen ez az új selected.
# Ha van selected, ami nem tud ide lépni akkor deselecteljük a bábut
# Ha nincs selected és olyan bábus mezőre kattintottunk amin a soron következő player bábuja áll akkor selecteljük.
# Ha nincs selected és a click nem selectelt semmit akkor nem kell csinálni semmit
# Az utolsó opción kívűl mindnél megakarjuk hívni a get_moves-t mert változott a selected
#def field_clicked(x,y):
    


# Boardot megkérdezzük melyik player áll a mezőn.
# Playert megkérdezzük milyen bábu áll a mezőn.
# Figurának meghívjuk a get_moves metódusát
#def get_moves(r,c,board):

#def get_player_moves(player)

# Új játékot indítunk
#def newgame():

# Ellenőrizzük vége van e már a játéknak
# Hány király van még játékban
# Ritkább és nem tudom kell e majd ez,
# de lépésismétlés illetve lépések száma ütés és gyalog mozgatás nélkül. Nem véletlenül van a FIDE szabályzatban.
#def is_game_over():


#def game_over():
def get_moves(figure, board):
    SIZE = 14

    board_targetset = [[0 for _ in range(SIZE)] for _ in range(SIZE)]

    r = figure.X
    c = figure.Y
    player_id = figure.Player

    board_targetset[r][c] = 1

    def in_bounds(nr, nc):
        return 0 <= nr < SIZE and 0 <= nc < SIZE

    def is_blocked(nr, nc):
        return board_fields[nr][nc] == -1

    def handle_square(nr, nc):
        occupant = board.board_state[nr][nc]
        if occupant == 0:
            board_targetset[nr][nc] = 2
            return True   # mehet tovább
        elif occupant == player_id:
            return False  # saját → stop
        else:
            board_targetset[nr][nc] = 3
            return False  # ütés után stop

    # ---------------- ROOK ----------------
    if figure.Type == Type.Rook:
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            while in_bounds(nr,nc) and not is_blocked(nr,nc):
                if not handle_square(nr,nc):
                    break
                nr += dr
                nc += dc

    # ---------------- BISHOP ----------------
    elif figure.Type == Type.Bishop:
        directions = [(-1,-1),(-1,1),(1,-1),(1,1)]
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            while in_bounds(nr,nc) and not is_blocked(nr,nc):
                if not handle_square(nr,nc):
                    break
                nr += dr
                nc += dc

    # ---------------- QUEEN ----------------
    elif figure.Type == Type.Queen:
        directions = [
            (-1,0),(1,0),(0,-1),(0,1),
            (-1,-1),(-1,1),(1,-1),(1,1)
        ]
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            while in_bounds(nr,nc) and not is_blocked(nr,nc):
                if not handle_square(nr,nc):
                    break
                nr += dr
                nc += dc

    # ---------------- KNIGHT ----------------
    elif figure.Type == Type.Knight:
        jumps = [
            (-2,-1),(-2,1),(2,-1),(2,1),
            (-1,-2),(-1,2),(1,-2),(1,2)
        ]
        for dr, dc in jumps:
            nr, nc = r+dr, c+dc
            if in_bounds(nr,nc) and not is_blocked(nr,nc):
                occupant = board.board_state[nr][nc]
                if occupant == 0:
                    board_targetset[nr][nc] = 2
                elif occupant != player_id:
                    board_targetset[nr][nc] = 3

    # ---------------- KING ----------------
    elif figure.Type == Type.King:
        directions = [
            (-1,0),(1,0),(0,-1),(0,1),
            (-1,-1),(-1,1),(1,-1),(1,1)
        ]
        for dr, dc in directions:
            nr, nc = r+dr, c+dc
            if in_bounds(nr,nc) and not is_blocked(nr,nc):
                occupant = board.board_state[nr][nc]
                if occupant == 0:
                    board_targetset[nr][nc] = 2
                elif occupant != player_id:
                    board_targetset[nr][nc] = 3

    # ---------------- PAWN ----------------
    elif figure.Type == Type.Pawn:

        directions = [ (1,0),(0,-1),(-1,0),(0,1) ]
        dr,dc = directions[player_id-1]

        # ---- 1 mezős előrelépés ----
        nr = r + dr
        nc = c + dc

        if in_bounds(nr, nc) and not is_blocked(nr, nc):
            if board.board_state[nr][nc] == 0:
                board_targetset[nr][nc] = 2

                # ---- 2 mezős (ha még nem mozdult) ----
                if not figure.HasMoved:
                    nr2 = r + 2*dr
                    nc2 = c + 2*dc

                    if in_bounds(nr2, nc2) and not is_blocked(nr2, nc2):
                        if board.board_state[nr2][nc2] == 0:
                            board_targetset[nr2][nc2] = 2

        # ---- Ütések ----
        side_dirs = [(-dc, dr), (dc, -dr)]

        for sdr, sdc in side_dirs:
            nr = r + dr + sdr
            nc = c + dc + sdc

            if in_bounds(nr, nc) and not is_blocked(nr, nc):
                occupant = board.board_state[nr][nc]
                if occupant != 0 and occupant != figure.Player:
                    board_targetset[nr][nc] = 3

    return board_targetset

    

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

    def __init__(self, rect: pg.Rect, rows, cols, board, player1, player2, player3, player4):
        super().__init__(rect)
        self.rows = rows; self.cols = cols
        self.board_targets = board_targets
        self.player1=player1
        self.player2=player2
        self.player3=player3
        self.player4=player4
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
        player=self.currentplayer()
        if ev.type==pg.MOUSEBUTTONDOWN and ev.button==1 and self.rect.collidepoint(ev.pos):
            mx,my = ev.pos
            pad, side, cell_size, board_px, board_py = self.compute_layout()
            rel_x = mx - board_px; rel_y = my - board_py
            col = int(rel_x // cell_size); row = int(rel_y // cell_size)
            if 0 <= row < self.rows and 0 <= col < self.cols and board_fields[row][col] != -1:

                entry = self.board.board_state[row][col]
                if entry == Current_Player and self.selected != (row,col):
                    Fig = player.get_figure(row, col)# type: ignore
                    if Fig is not None:
                        self.selected = (row, col)
                        self.board_targets = get_moves(Fig, self.board)
                else:
                    self.selected = None
                    self.board_targets = [[0]*14 for _ in range(14)]
                print("Board clicked cell:", (row,col))
            else:
                print("Click outside playable board or on OOB cell.")

    def currentplayer(self):
        match Current_Player:
                    case 1:
                        return self.player1
                    case 2:
                        return self.player2
                    case 3:
                        return self.player3
                    case 4:
                        return self.player4
    
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
                match self.board_targets[r][c]:
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
                player=self.player1
                match entry:
                    case 1:
                        player=self.player1
                    case 2:
                        player=self.player2
                    case 3:
                        player=self.player3
                    case 4:
                        player=self.player4
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
        self.board=Board()
        self.board.setupboard_state(self.player1, self.player2, self.player3, self.player4 )
        # UI elements lesznek frameenként újraszámolva rect alapján
        # board wrapper (tárolja a piece_grid és board_fields)
        self.board_panel = BoardField(pg.Rect(0,0,100,100), BOARD_ROWS, BOARD_COLS, self.board, self.player1, self.player2, self.player3, self.player4)
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
    
    
