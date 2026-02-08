import pygame as pg
from pygame import freetype
import sys
from Persistence import *
import pygame.freetype as ft

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

# board méret (14x14, ahogy te definiáltad)
BOARD_ROWS = 14
BOARD_COLS = 14




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
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
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



    
# click event
# Ablak átméretezés kedvéért relatív méretet használok.
#x<0.1 menüsör nézzük meg a menügombokat, hogy meglettek-e enyomva
#x>0.9 státuszsor nincs interakció
#egyébb akkor a click a játékteret érintette, nézzük meg melyik mező lett megnyomva, ha mező volt.
def main():
    pg.init()
    pg.display.set_caption("4-player chess")

    screen = pg.display.set_mode((WINDOW_W, WINDOW_H), pg.RESIZABLE)
    clock = pg.time.Clock()

    font_name = "DejaVu Sans"
    try:
        ft_font = ft.SysFont(font_name, 36)
    except Exception:
        ft_font = ft.SysFont(None, 36)
    running = True

    selected_cell = None

    while running:
        dt = clock.tick(FPS)
        w, h = screen.get_size()

        # panel méretek abszolútban (pixel)
        left_w = int(w * LEFT_PANEL_RATIO)
        right_w = w - left_w
        top_h = 0
        bottom_h = 40

        # menü bal panel (input, player adatok)
        left_rect = pg.Rect(0, 0, left_w, h - bottom_h)
        # tábla panel jobb oldalon
        board_rect = pg.Rect(left_w, 0, right_w, h - bottom_h)
        status_rect = pg.Rect(0, h - bottom_h, w, bottom_h)

        # események
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                running = False
            elif ev.type == pg.VIDEORESIZE:
                # új mérethez az ablak frissítése
                screen = pg.display.set_mode((ev.w, ev.h), pg.RESIZABLE)
            elif ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                mx, my = ev.pos
                # menüsor: left_rect, státusz: status_rect, egyéb: board_rect
                if left_rect.collidepoint((mx, my)):
                    print("Menü")
                elif status_rect.collidepoint((mx, my)):
                    print("Státuszsor")
                elif board_rect.collidepoint((mx, my)):
                    # használjuk ugyanazt a számítást, mint a rendernél: board_side, cell_size, board_px, board_py
                    padding_pixels = max(8, int(min(board_rect.width, board_rect.height) * 0.02))
                    board_side = min(board_rect.width, board_rect.height) - 2 * padding_pixels
                    if board_side <= 0:
                        board_side = min(board_rect.width, board_rect.height)
                    cell_size = board_side / BOARD_COLS
                    board_px = board_rect.x + (board_rect.width - board_side) / 2
                    board_py = board_rect.y + (board_rect.height - board_side) / 2

                    rel_x = mx - board_px
                    rel_y = my - board_py
                    col = int(rel_x // cell_size)
                    row = int(rel_y // cell_size)
                    if 0 <= row < BOARD_ROWS and 0 <= col < BOARD_COLS and board_fields[row][col] != -1:
                        print("Kattintott mezo:", (row, col))
                        if selected_cell == (row, col):
                            selected_cell = None
                        else:
                            selected_cell = (row, col)
                    else:
                        print("Nem mezo")
                else:
                    print(" ")

        # ---------- RENDER ----------
        screen.fill((30, 30, 30))  #háttér

        # Bal panel
        pg.draw.rect(screen, (40, 40, 40), left_rect)
        # Menü gombok
        btn_h = 30
        btn_w = left_rect.width - 20
        for i, txt in enumerate(["New Game", "Save Game", "Load Game"]):
            btn_rect = pg.Rect(left_rect.x + 10, left_rect.y + 10 + i*(btn_h + 8), btn_w, btn_h)
            pg.draw.rect(screen, (70, 70, 70), btn_rect, border_radius=4)
            ft.SysFont(None, 18).render_to(screen, (btn_rect.x + 8, btn_rect.y + 6), txt, fgcolor=(230,230,230))

        # Board háttér
        pg.draw.rect(screen, (60, 60, 60), board_rect)

        # számoljuk cell_size-ot és board origin-t úgy, hogy a board legyen négyzet és legyen padding
        # padding a jobb panelen belül (pixelben)
        padding_pixels = max(8, int(min(board_rect.width, board_rect.height) * 0.02))

        # a board "side" legyen a rendelkezésre álló hely legkisebb oldala, minusz a padding
        board_side = min(board_rect.width, board_rect.height) - 2 * padding_pixels
        if board_side <= 0:
            board_side = min(board_rect.width, board_rect.height)  # fallback

        cell_size = board_side / BOARD_COLS

        # középre igazítjuk a négyzetes táblát a jobb panelon belül, megtartva a paddinget
        board_px = board_rect.x + (board_rect.width - board_side) / 2
        board_py = board_rect.y + (board_rect.height - board_side) / 2

        for r in range(BOARD_ROWS):
            for c in range(BOARD_COLS):
                bf = board_fields[r][c]
                if bf == -1:
                    continue
                sq_x = int(board_px + c*cell_size)
                sq_y = int(board_py + r*cell_size)
                rect = pg.Rect(sq_x, sq_y, int(cell_size)+1, int(cell_size)+1)
                color = SQUARE_DARK if bf == 1 else SQUARE_LIGHT
                pg.draw.rect(screen, color, rect)



                # Körvonal a selected_cell-hez. Később a get_moves al a lehetséges moveoknak is.
                if selected_cell == (r, c):
                    pg.draw.rect(screen, (0,120,0), rect, width=4)

        pg.draw.rect(screen, (50,50,50), status_rect)
        status_text = f"Selected: {selected_cell}    Window: {w}x{h}"
        ft.SysFont(None, 18).render_to(screen, (10, status_rect.y + 8), status_text, fgcolor=(230,230,230))

        pg.display.flip()

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()

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
#def get_moves(x,y):

# Új játékot indítunk
#def newgame():

# Ellenőrizzük vége van e már a játéknak
# Hány király van még játékban
# Ritkább és nem tudom kell e majd ez,
# de lépésismétlés illetve lépések száma ütés és gyalog mozgatás nélkül. Nem véletlenül van a FIDE szabályzatban.
#def is_game_over():


#def game_over():