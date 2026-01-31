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
        self.setup_player1(player1)
        self.setup_player2(player2)
        self.setup_player3(player3)
        self.setup_player4(player4)


    def setup_player1(self, player):
        for i in range(8):
            player.add_figure(Figure(1, i+3, Type.Pawn))
            self.board_state[1][i+3]=FieldState.Player1
            self.board_state[0][i+3]=FieldState.Player1
        player.add_figure(Figure(0, 3, Type.Rook))
        player.add_figure(Figure(0, 10, Type.Rook))
        player.add_figure(Figure(0, 4, Type.Knight))
        player.add_figure(Figure(0, 9, Type.Knight))
        player.add_figure(Figure(0, 5, Type.Bishop))
        player.add_figure(Figure(0, 8, Type.Bishop))
        player.add_figure(Figure(0, 6, Type.King))
        player.add_figure(Figure(0, 7, Type.Queen))
        

    def setup_player2(self, player):
        for i in range(8):
            player.add_figure(Figure(i+3, 1, Type.Pawn))
            self.board_state[i+3][1]=FieldState.Player2
            self.board_state[i+3][0]=FieldState.Player2
        player.add_figure(Figure(3, 0, Type.Rook))
        player.add_figure(Figure(10, 0, Type.Rook))
        player.add_figure(Figure(4, 0, Type.Knight))
        player.add_figure(Figure(9, 0, Type.Knight))
        player.add_figure(Figure(5, 0, Type.Bishop))
        player.add_figure(Figure(8, 0, Type.Bishop))
        player.add_figure(Figure(6, 0, Type.King))
        player.add_figure(Figure(7, 0, Type.Queen))

    def setup_player3(self, player):
        for i in range(8):
            player.add_figure(Figure(12, i+3, Type.Pawn))
            self.board_state[12][i+3]=FieldState.Player3
            self.board_state[13][i+3]=FieldState.Player3
        player.add_figure(Figure(13, 3, Type.Rook))
        player.add_figure(Figure(13, 10, Type.Rook))
        player.add_figure(Figure(13, 4, Type.Knight))
        player.add_figure(Figure(13, 9, Type.Knight))
        player.add_figure(Figure(13, 5, Type.Bishop))
        player.add_figure(Figure(13, 8, Type.Bishop))
        player.add_figure(Figure(13, 6, Type.Queen))
        player.add_figure(Figure(13, 7, Type.King))

    def setup_player4(self, player):
        for i in range(8):
            player.add_figure(Figure(i+3, 12, Type.Pawn))
            self.board_state[i+3][12]=FieldState.Player4
            self.board_state[i+3][13]=FieldState.Player4
        player.add_figure(Figure(3, 13, Type.Rook))
        player.add_figure(Figure(10, 13, Type.Rook))
        player.add_figure(Figure(4, 13, Type.Knight))
        player.add_figure(Figure(9, 13, Type.Knight))
        player.add_figure(Figure(5, 13, Type.Bishop))
        player.add_figure(Figure(8, 13, Type.Bishop))
        player.add_figure(Figure(6, 13, Type.Queen))
        player.add_figure(Figure(7, 13, Type.King))
        
    