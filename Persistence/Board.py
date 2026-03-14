from dataclasses import dataclass
from .Figure import Figure
from .Player import Player
from .Type import Type
import numpy as np

@dataclass(frozen=True)
class Action:
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    special: object = None

Fig_value_scale=0.02
    
try:
    import torch
    _HAS_TORCH = True
except Exception:
    _HAS_TORCH = False

class Board:
    def __init__(self,player1,player2,player3,player4):
        self.board_state = self.empty_board()
        self.msg=""
        self.ispromoting=False
        self.player1=player1
        self.player2=player2
        self.player3=player3
        self.player4=player4
        self.current_player_index=1
        self.is_game_over=False
        self.move_number=1
        self.board_targets=self.empty_board()
        self.selected_figure = None
        self.current_actions: list[Action] = []
        self.action_lookup: dict[tuple[int,int], list[Action]] = {}
    
    def newgame(self):
        self.board_state = self.empty_board()
        self.is_game_over=False
        self.move_number=1
        self.ispromoting=False
        self.msg=""
        self.player1.startposition()
        self.player2.startposition()
        self.player3.startposition()
        self.player4.startposition()
        self.setupboard_state()
        self.current_player_index=1
        self.board_targets=self.empty_board()
        
    
    def setupboard_state(self):
        self.setup_player_state(self.player1, 1)
        self.setup_player_state(self.player2, 2)
        self.setup_player_state(self.player3, 3)
        self.setup_player_state(self.player4, 4)
    
    def setup_player_state(self, player, field_state):
        for pos in player.get_figure_pos_list():  
            x, y = pos
            self.board_state[x][y] = field_state
    
    def get_player(self, which) -> Player: # type: ignore
        match which:
            case 1:
                return self.player1
            case 2:
                return self.player2
            case 3:
                return self.player3
            case 4:
                return self.player4
    
    def get_current_player(self) -> Player:
        return self.get_player(self.current_player_index)
    

    def get_figure(self,x,y) -> Figure:
        p=self.board_state[x][y]
        player=self.get_player(p)
        return player.get_figure(x,y) # type: ignore
    

    def ispromotion(self, row, col, player_id) -> bool:
        if row==0 or row==13 or col==0 or col==13:
                return True
        if (player_id==1 and row>=7)or (player_id==2 and col<=6) or (player_id==3 and row<=6) or (player_id==4 and col>=7):
            return True
        return False
    
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


    def select_figure(self, x, y):
        fig = self.get_figure(x, y)
        if fig is None:
            self.selected_figure = None
            self.current_actions = []
            self.action_lookup = {}
            self.board_targets = self.empty_board()
            return
        print(fig.HasMoved)
        self.selected_figure = fig
        self.current_actions = self.get_moves(fig)

        self.action_lookup = {}
        for a in self.current_actions:
            key = (a.to_row, a.to_col)
            self.action_lookup.setdefault(key, []).append(a)
        self.board_targets = self.actions_to_board_targets(self.current_actions)


    def resolve_action_by_target(self, to_row: int, to_col: int) -> Action | None:
        lst = self.action_lookup.get((to_row, to_col))
        if not lst:
            return None
        if len(lst) == 1:
            return lst[0]
        return lst[0]


    def get_moves(self, figure: Figure):
        SIZE = 14
        actions = []

        r = figure.X
        c = figure.Y
        player_id = figure.Player
        player =self.get_player(player_id)
        def in_bounds(nr, nc):
            return 0 <= nr < SIZE and 0 <= nc < SIZE

        def is_blocked(nr, nc):
            return self.board_state[nr][nc] == -1

        def handle_square_for_slides(nr, nc):
            occupant = self.board_state[nr][nc]
            if occupant == 0:
                actions.append(Action(r, c, nr, nc, None))
                return True   # keep sliding
            elif occupant == player_id:
                return False  # own piece -> stop
            else:
                actions.append(Action(r, c, nr, nc, "capture"))
                return False  # capture -> stop

        # ---------------- ROOK ----------------
        if figure.Type == Type.Rook:
            directions = [(-1,0),(1,0),(0,-1),(0,1)]
            for dr, dc in directions:
                nr, nc = r+dr, c+dc
                while in_bounds(nr,nc) and not is_blocked(nr,nc):
                    if not handle_square_for_slides(nr,nc):
                        break
                    nr += dr
                    nc += dc

        # ---------------- BISHOP ----------------
        elif figure.Type == Type.Bishop:
            directions = [(-1,-1),(-1,1),(1,-1),(1,1)]
            for dr, dc in directions:
                nr, nc = r+dr, c+dc
                while in_bounds(nr,nc) and not is_blocked(nr,nc):
                    if not handle_square_for_slides(nr,nc):
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
                    if not handle_square_for_slides(nr,nc):
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
                        actions.append(Action(r, c, nr, nc, None))
                    elif occupant != player_id:
                        actions.append(Action(r, c, nr, nc, "capture"))

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
                        actions.append(Action(r, c, nr, nc, None))
                    elif occupant != player_id:
                        actions.append(Action(r, c, nr, nc, "capture"))
            # ---------------- KingCastle ----------------
            if figure.HasMoved==False:
                match player_id:
                    case 1:
                        if self.board_state[0][4]==0 and self.board_state[0][5]==0:
                            if self.board_state[0][3]==player_id:
                                F= player.get_figure(0,3) # type: ignore
                                if F.Type==Type.Rook and F.HasMoved==False:
                                    actions.append(Action(r, c, 0, 4, "KingCastle"))
                    case 4:
                        if self.board_state[5][0]==0 and self.board_state[4][0]==0:
                            if self.board_state[3][0]==player_id:
                                F= player.get_figure(3,0) # type: ignore
                                if F.Type==Type.Rook and F.HasMoved==False:
                                    actions.append(Action(r, c, 4, 0, "KingCastle"))
                    case 2:
                        if self.board_state[8][13]==0 and self.board_state[9][13]==0:
                            if self.board_state[10][13]==player_id:
                                F= player.get_figure(10,13) # type: ignore
                                if F.Type==Type.Rook and F.HasMoved==False:
                                    actions.append(Action(r, c, 9, 13, "KingCastle"))
                    case 3:
                        if self.board_state[13][8]==0 and self.board_state[13][9]==0:
                            if self.board_state[13][10]==player_id:
                                F= player.get_figure(13,10) # type: ignore
                                if F.Type==Type.Rook and F.HasMoved==False:
                                    actions.append(Action(r, c, 13, 9, "KingCastle"))
            # ---------------- QueenCastle ----------------
            if figure.HasMoved==False:
                match player_id:
                    case 1:
                        if self.board_state[0][7]==0 and self.board_state[0][8]==0 and self.board_state[0][9]==0:
                            if self.board_state[0][10]==player_id:
                                F= player.get_figure(0,10) # type: ignore
                                if F.Type==Type.Rook and F.HasMoved==False:
                                    actions.append(Action(r, c, 0, 8, "QueenCastle"))
                    case 4:
                        if self.board_state[7][0]==0 and self.board_state[8][0]==0 and self.board_state[9][0]==0:
                            if self.board_state[10][0]==player_id:
                                F= player.get_figure(10,0) # type: ignore
                                if F.Type==Type.Rook and F.HasMoved==False:
                                    actions.append(Action(r, c, 8, 0, "QueenCastle"))
                    case 2:
                        if self.board_state[6][13]==0 and self.board_state[5][13]==0 and self.board_state[4][13]==0:
                            if self.board_state[3][13]==player_id:
                                F= player.get_figure(3,13) # type: ignore
                                if F.Type==Type.Rook and F.HasMoved==False:
                                    actions.append(Action(r, c, 5, 13, "QueenCastle"))
                    case 3:
                        if self.board_state[13][6]==0 and self.board_state[13][5]==0 and self.board_state[13][4]==0:
                            if self.board_state[13][3]==player_id:
                                F= player.get_figure(13,3) # type: ignore
                                if F.Type==Type.Rook and F.HasMoved==False:
                                    actions.append(Action(r, c, 13, 5, "QueenCastle"))                                
                            
            

        # ---------------- PAWN ----------------
        elif figure.Type == Type.Pawn:
            directions = [ (1,0),(0,-1),(-1,0),(0,1) ]
            dr,dc = directions[player_id-1]
            actn=None
            nr = r + dr
            nc = c + dc
            if in_bounds(nr, nc) and not is_blocked(nr, nc):
                if self.board_state[nr][nc] == 0:
                    if self.ispromotion(nr,nc,player_id):
                        actn="Promotion"
                    actions.append(Action(r, c, nr, nc, actn))


                    if not figure.HasMoved:
                        nr2 = r + 2*dr
                        nc2 = c + 2*dc
                        if in_bounds(nr2, nc2) and not is_blocked(nr2, nc2):
                            if self.board_state[nr2][nc2] == 0:
                                actions.append(Action(r, c, nr2, nc2, "double"))

            side_dirs = [(-dc, dr), (dc, -dr)]
            for sdr, sdc in side_dirs:
                nr = r + dr + sdr
                nc = c + dc + sdc
                if in_bounds(nr, nc) and not is_blocked(nr, nc):
                    occupant = self.board_state[nr][nc]
                    if occupant != 0 and occupant != figure.Player:
                        if self.ispromotion(nr,nc,player_id):
                            actn="Promotion"
                        actions.append(Action(r, c, nr, nc, actn))

        return actions
    
    
    # a kiválasztott bábu melyik mezőkre tud lépni illetve ütni
    # -1 nem a tábla része
    # 0 nem érintett mező nincs keret/fekete keret 
    # 1 kiválasztott bábu itt áll mező sötét zöld keret
    # 2 kiválasztott bábu ide tud lépni, világosabb zöld keret
    # 3 kiválasztott bábu az itt álló bábut ütni tudja piros keret
    # 4 kiválasztott gyalog ha idelép akkor előléptetődik
    def actions_to_board_targets(self, actions, highlight_from=True):
        board_targetset = self.empty_board()
        for a in actions:
            if highlight_from:
                board_targetset[a.from_row][a.from_col] = 1
            if a.special == "promotion":
                board_targetset[a.to_row][a.to_col] = 4
            else:
                if 0 <= a.to_row < len(board_targetset) and 0 <= a.to_col < len(board_targetset[0]):
                    occupant = self.board_state[a.to_row][a.to_col]
                    if occupant != 0 and occupant != self.board_state[a.from_row][a.from_col]:
                        board_targetset[a.to_row][a.to_col] = 3
                    else:
                        board_targetset[a.to_row][a.to_col] = 2
                    fromrow,fromcol=a.from_row,a.from_col
                    p=self.board_state[fromrow][fromcol]
                    if self.ispromotion(a.to_row, a.to_col,p ):
                        if self.get_figure(fromrow,fromcol).Type==Type.Pawn:
                            board_targetset[a.to_row][a.to_col] = 4
        return board_targetset
    
    def get_all_moves(self, player_index: int):
        moves = []
        player = self.get_player(player_index)
        for pos in player.get_figure_pos_list(): # type: ignore
            r, c = pos
            fig = player.get_figure(r, c) # type: ignore
            if fig is None:
                continue
            fig_actions = self.get_moves(fig)
            moves.extend(fig_actions)
        return moves
    
    def make_hitmap(self, player_id):
        hitmap = self.empty_board()
        opponent_actions= []
        for i in range(1,5):
            if i == player_id or self.get_player(i).IsDefeated: # type: ignore
                continue
            player_actions=self.get_all_moves(i)
            opponent_actions.extend(player_actions)
        for action in opponent_actions:
            row, col = action.from_row, action.from_col
            newrow, newcol = action.to_row, action.to_col
            fig=self.get_figure(row,col)
            type=fig.Type 
            if hitmap[newrow][newcol]==0:
                hitmap[newrow][newcol]=type.value
            elif hitmap[newrow][newcol]>0:
                hitmap[newrow][newcol]=min(hitmap[newrow][newcol], type.value)
        return hitmap 
    
    def make_protectmap(self, player_id):
        protectmap=self.empty_board()
        actions=self.get_all_moves(player_id)
        for action in actions:
            newrow, newcol = action.to_row, action.to_col
            protectmap[newrow][newcol]=1
        return protectmap
        


    def make_move(self, action: Action):
        row, col = action.from_row, action.from_col
        newrow, newcol = action.to_row, action.to_col
        reward=0
        p1 = self.board_state[row][col]
        if p1 == 0:
            print("ERROR: Nincs bábu a mezőn")
            return
        player1 = self.get_player(p1)
        Fig1 = player1.get_figure(row, col)   # type: ignore
        if Fig1 is None:
            print("ERROR: játékosnak nincs ilyen bábuja")
            return


        p2 = self.board_state[newrow][newcol]
        if p2 > 0 and p2 != p1:
            player2 = self.get_player(p2)
            Fig2 = player2.get_figure(newrow, newcol)  # type: ignore
            if Fig2 is not None:
                if Fig2.Type == Type.King:
                    player2.IsDefeated = True  # type: ignore
                    self.msg=f"PLAYER {p2} is Defeated"
                reward= reward+ Fig2.Type.value*Fig_value_scale
                player2.remove_figure(Fig2)  # type: ignore

        # remove from current player container, move, add back
        player1.remove_figure(Fig1)  # type: ignore
        Fig1.move(newrow, newcol)
        player1.add_figure(Fig1)  # type: ignore

        # update board_state grid
        self.board_state[newrow][newcol] = p1
        self.board_state[row][col] = 0
        
        if action.special =="Promotion":
            reward = reward + (Fig1.Type.value-1)* Fig_value_scale
        
        if action.special=="KingCastle":
            rookrow,rookcol=0,0
            newrookrow,newrookcol=0,0
            if row-newrow==2:
                rookrow,rookcol=3,0
                newrookrow,newrookcol=5,0
            if row-newrow==-2:
                rookrow,rookcol=10,13
                newrookrow,newrookcol=8,13
            if col-newcol==2:
                rookrow,rookcol=0,3
                newrookrow,newrookcol=0,5
            if col-newcol==-2:
                rookrow,rookcol=13,10
                newrookrow,newrookcol=13,8
            Fig3=player1.get_figure(rookrow,rookcol) # type: ignore
            player1.remove_figure(Fig3) # type: ignore
            Fig3.move(newrookrow,newrookcol)
            player1.add_figure(Fig3) # type: ignore
            self.board_state[newrookrow][newrookcol] = p1
            self.board_state[rookrow][rookcol] = 0
            reward=reward+0.01
            
        if action.special=="QueenCastle":
            rookrow,rookcol=0,0
            newrookrow,newrookcol=0,0
            if row-newrow==2:
                rookrow,rookcol=3,13
                newrookrow,newrookcol=6,13
            if row-newrow==-2:
                rookrow,rookcol=10,0
                newrookrow,newrookcol=7,0
            if col-newcol==2:
                rookrow,rookcol=13,3
                newrookrow,newrookcol=13,6
            if col-newcol==-2:
                rookrow,rookcol=0,10
                newrookrow,newrookcol=0,7
            Fig3=player1.get_figure(rookrow,rookcol) # type: ignore
            player1.remove_figure(Fig3) # type: ignore
            Fig3.move(newrookrow,newrookcol)
            player1.add_figure(Fig3) # type: ignore
            self.board_state[newrookrow][newrookcol] = p1
            self.board_state[rookrow][rookcol] = 0
            reward=reward+0.01
        
        hitmap=self.make_hitmap(p1)
        protectmap=self.make_protectmap(p1)
        hit_value=hitmap[newrow][newcol]
        if hit_value>0:
            if protectmap[newrow][newcol]==1:
                reward = reward - min(0,hit_value-Fig1.Type.value)*Fig_value_scale
            else:
                reward = reward - Fig1.Type.value * Fig_value_scale
        self.get_player(p1).Reward = reward # type: ignore
        self.next_player()
        
    def try_move(self, to_row: int, to_col: int) -> bool:
        action = self.resolve_action_by_target(to_row, to_col)
        if action is None:
            return False
        
        self.make_move(action)
        self.selected_figure = None
        self.current_actions = []
        self.action_lookup = {}
        self.board_targets = self.empty_board()
        return True
   
    def next_player(self):
        start=self.current_player_index
        next = self.current_player_index+1
        if next==5:
            next=1
            self.move_number=self.move_number+1
        print("start",start)
        while self.get_player(next).IsDefeated: # type: ignore
            next=next+1
            if next==5:
                self.move_number=self.move_number+1
                next=1
            print("next:",next)
            if(next==start):
                self.is_game_over=True
                print("GAME OVER, player",start,"won")
                self.msg=f"PLAYER {start} WON"
                return
            
        self.current_player_index=next







    def encode_state(self, include_extras=True):  
        H, W = 14, 14
        # C*H*W = 29*14*14 3d numpy Tenzor
        # minden játékos minden figura típusához layer, 4*6=24
        #4 layer one-hot encoding, melyik player van soron
        #1 layer ahol mező értéke 1, ha még nem mozgott. sánc, gyalog duplalépés ilyesmi
        # channel count here: 24 + 4 + 1 = 29
        C = 29
        tensor = np.zeros((C, H, W), dtype=np.float32)
        # figura typusok sorrendje
        piece_index = {
            Type.Pawn: 0,
            Type.Knight: 1,
            Type.Bishop: 2,
            Type.Rook: 3,
            Type.Queen: 4,
            Type.King: 5
        }

        for player_id in range(1, 5):
            player = self.get_player(player_id)
            for pos in player.get_figure_pos_list():  # type: ignore
                r, c = pos
                fig = player.get_figure(r, c)  # type: ignore
                if fig is None:
                    continue
                pidx = piece_index.get(fig.Type, None)
                if pidx is None:
                    continue
                chan = (player_id - 1) * 6 + pidx
                tensor[chan, r, c] = 1.0
                if include_extras and getattr(fig, "HasMoved", False):
                    tensor[28, r, c] = 1.0

        cur = self.current_player_index
        if 1 <= cur <= 4:
            tensor[24 + (cur - 1), :, :] = 1.0


        return tensor



