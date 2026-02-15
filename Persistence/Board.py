from .Figure import Figure
from .Type import Type
class Board:
    def __init__(self):
        self.board_state = [[-1] * 14 for _ in range(14)]
        for i in range(2,12):
            for j in range(2,12):
                self.board_state[i][j]=0
        self.board_state[2][2]=-1
        self.board_state[2][11]=-1
        self.board_state[11][2]=-1
        self.board_state[11][11]=-1
    
    def setupboard_state(self, player1, player2, player3, player4):
        self.setup_player_state(player1, 1)
        self.setup_player_state(player2, 2)
        self.setup_player_state(player3, 3)
        self.setup_player_state(player4, 4)
    
    def setup_player_state(self, player, field_state):
        for pos in player.get_figure_pos_list():  
            x, y = pos
            self.board_state[x][y] = field_state
