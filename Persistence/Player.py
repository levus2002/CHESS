from .Figure import Figure
from .Type import Type
class Player():
    def __init__(self, which_player, color, name=None):
        self.IsDefeated = False
        self.Score = 0
        self.Figures: dict[tuple[int, int], Figure] = {}
        self.Color = color
        self.Which_Player = which_player
        self.name = name if name is not None else f"Player{which_player}"
        match which_player:
            case 1:
                self.setup_player1()
            case 2:
                self.setup_player2()
            case 3:
                self.setup_player3()
            case 4:
                self.setup_player4()
    def add_figure(self, figure):
        self.Figures[(figure.X, figure.Y)] = figure
    # Milyen figura van x,y pozición, ha nincs akkor None
    def get_figure(self,x,y):
        return self.Figures.get((x, y))
    
    #return list of figure positions    
    def get_figure_pos_list(self):
        return list(self.Figures.keys())
    
    #kiürítjük Figures listát
    def empty_figures(self):
        self.Figures.clear()
    
    # hívjuk meg minden figurára a Figure osztály get_moves-át 

        
    #állítsuk be a Player adatait fájlból beolvasva
    #def load_figures
    
    #mentsük el plaayer adatait fájlba
    #def save_figures
    
    
    def setup_player1(self):
        for i in range(8):
            self.add_figure(Figure(1, i+3, Type.Pawn, 1))
        self.add_figure(Figure(0, 3, Type.Rook, 1))
        self.add_figure(Figure(0, 10, Type.Rook, 1))
        self.add_figure(Figure(0, 4, Type.Knight, 1))
        self.add_figure(Figure(0, 9, Type.Knight, 1))
        self.add_figure(Figure(0, 5, Type.Bishop, 1))
        self.add_figure(Figure(0, 8, Type.Bishop, 1))
        self.add_figure(Figure(0, 6, Type.King, 1))
        self.add_figure(Figure(0, 7, Type.Queen, 1))
        

    def setup_player2(self):
        for i in range(8):
            self.add_figure(Figure(i+3, 1, Type.Pawn, 2))
        self.add_figure(Figure(3, 0, Type.Rook, 2))
        self.add_figure(Figure(10, 0, Type.Rook, 2))
        self.add_figure(Figure(4, 0, Type.Knight, 2))
        self.add_figure(Figure(9, 0, Type.Knight, 2))
        self.add_figure(Figure(5, 0, Type.Bishop, 2))
        self.add_figure(Figure(8, 0, Type.Bishop, 2))
        self.add_figure(Figure(6, 0, Type.King, 2))
        self.add_figure(Figure(7, 0, Type.Queen, 2))

    def setup_player3(self):
        for i in range(8):
            self.add_figure(Figure(12, i+3, Type.Pawn, 3))
        self.add_figure(Figure(13, 3, Type.Rook, 3))
        self.add_figure(Figure(13, 10, Type.Rook, 3))
        self.add_figure(Figure(13, 4, Type.Knight, 3))
        self.add_figure(Figure(13, 9, Type.Knight, 3))
        self.add_figure(Figure(13, 5, Type.Bishop, 3))
        self.add_figure(Figure(13, 8, Type.Bishop, 3))
        self.add_figure(Figure(13, 6, Type.Queen, 3))
        self.add_figure(Figure(13, 7, Type.King, 3))

    def setup_player4(self):
        for i in range(8):
            self.add_figure(Figure(i+3, 12, Type.Pawn, 4))
        self.add_figure(Figure(3, 13, Type.Rook, 4))
        self.add_figure(Figure(10, 13, Type.Rook, 4))
        self.add_figure(Figure(4, 13, Type.Knight, 4))
        self.add_figure(Figure(9, 13, Type.Knight, 4))
        self.add_figure(Figure(5, 13, Type.Bishop, 4))
        self.add_figure(Figure(8, 13, Type.Bishop, 4))
        self.add_figure(Figure(6, 13, Type.Queen, 4))
        self.add_figure(Figure(7, 13, Type.King, 4))
    