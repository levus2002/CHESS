from .Figure import Figure
from .Type import Type
class Board:
    def __init__(self,player1,player2,player3,player4):
        self.board_state = self.empty_board()
        self.player1=player1
        self.player2=player2
        self.player3=player3
        self.player4=player4
        self.current_player_index=1
        self.is_game_over=False
        self.setupboard_state()
        self.board_targets=self.empty_board()
    
    #def newgame(self):
        
        
    
    def setupboard_state(self):
        self.setup_player_state(self.player1, 1)
        self.setup_player_state(self.player2, 2)
        self.setup_player_state(self.player3, 3)
        self.setup_player_state(self.player4, 4)
    
    def setup_player_state(self, player, field_state):
        for pos in player.get_figure_pos_list():  
            x, y = pos
            self.board_state[x][y] = field_state
    
    def get_player(self, which):
        match which:
            case 1:
                return self.player1
            case 2:
                return self.player2
            case 3:
                return self.player3
            case 4:
                return self.player4
    
    def get_current_player(self):
        return self.get_player(self.current_player_index)
    
    def next_player(self):
        start=self.current_player_index
        next = self.current_player_index+1
        if next==5:
            next=1
        print("start",start)
        while self.get_player(next).IsDefeated: # type: ignore
            next=next+1
            if next==5:
                next=1
            print("next:",next)
            if(next==start):
                self.is_game_over=True
                print("GAME OVER, player",start,"won")
                return
            
        self.current_player_index=next


    def get_moves(self, figure):
        SIZE = 14

        board_targetset = self.empty_board()

        r = figure.X
        c = figure.Y
        player_id = figure.Player

        board_targetset[r][c] = 1

        def in_bounds(nr, nc):
            return 0 <= nr < SIZE and 0 <= nc < SIZE

        def is_blocked(nr, nc):
            return board_targetset[nr][nc] == -1

        def handle_square(nr, nc):
            occupant = self.board_state[nr][nc]
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
                    occupant = self.board_state[nr][nc]
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
                    occupant = self.board_state[nr][nc]
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
                if self.board_state[nr][nc] == 0:
                    board_targetset[nr][nc] = 2

                    # ---- 2 mezős (ha még nem mozdult) ----
                    if not figure.HasMoved:
                        nr2 = r + 2*dr
                        nc2 = c + 2*dc

                        if in_bounds(nr2, nc2) and not is_blocked(nr2, nc2):
                            if self.board_state[nr2][nc2] == 0:
                                board_targetset[nr2][nc2] = 2

            # ---- Ütések ----
            side_dirs = [(-dc, dr), (dc, -dr)]

            for sdr, sdc in side_dirs:
                nr = r + dr + sdr
                nc = c + dc + sdc

                if in_bounds(nr, nc) and not is_blocked(nr, nc):
                    occupant = self.board_state[nr][nc]
                    if occupant != 0 and occupant != figure.Player:
                        board_targetset[nr][nc] = 3

        return board_targetset
    
    
    # a kiválasztott bábu melyik mezőkre tud lépni illetve ütni
    # -1 nem a tábla része
    # 0 nem érintett mező nincs keret/fekete keret 
    # 1 kiválasztott bábu itt áll mező sötét zöld keret
    # 2 kiválasztott bábu ide tud lépni, világosabb zöld keret
    # 3 kiválasztott bábu az itt álló bábu ütni tudja piros keret
    def empty_board(self):
        return [
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


    def make_move(self, row, col, newrow, newcol):
        p1=self.board_state[row][col]
        player1=self.get_player(p1)
        Fig1=player1.get_figure(row,col) # type: ignore
        if Fig1 is None:
            print("ERROR: Nincs bábu a mezőn")
            return
        player1.remove_figure(Fig1) # type: ignore
        Fig1.move(newrow,newcol)
        player1.add_figure(Fig1) # type: ignore
        
        p2=self.board_state[newrow][newcol]
        if p2==p1:
            print("ERROR saját bábu áll a mezőn ")
        if p2>0:
            player2=self.get_player(p2)
            Fig2=player2.get_figure(newrow,newcol)  # type: ignore
            if Fig2.Type == Type.King:
                player2.IsDefeated=True    # type: ignore
            player2.remove_figure(Fig2) # type: ignore
        
        self.board_state[newrow][newcol]=p1
        self.board_state[row][col]=0
        self.next_player()
