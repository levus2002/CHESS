from FieldState import FieldState
from Figure import Figure
from Player import Player
from Type import Type
class Board:
    #tábla alakja, hogy megjelenítésnek ne kelljen számolnia
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
    
    
    def __init__(self):
        self.board_state = [[FieldState.OutOFBounds] * 14 for _ in range(14)]
        for i in range(2,12):
            for j in range(2,12):
                self.board_state[i][j]=FieldState.Empty
        self.board_state[2][2]=FieldState.OutOFBounds
        self.board_state[2][11]=FieldState.OutOFBounds
        self.board_state[11][2]=FieldState.OutOFBounds
        self.board_state[11][11]=FieldState.OutOFBounds
    
    def setupboard_state(self, player1, player2, player3, player4):
        self.setup_player_state(player1, FieldState.Player1)
        self.setup_player_state(player2, FieldState.Player2)
        self.setup_player_state(player3, FieldState.Player3)
        self.setup_player_state(player4, FieldState.Player4)
    
    def setup_player_state(self, player, field_state):
        for pos in player.get_figure_pos_list():  
            x, y = pos
            self.board_state[x][y] = field_state
