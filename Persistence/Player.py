from .Figure import Figure
class Player():
    def __init__(self, which_player,control="manual",color=None,start_time_sec=900, name=None):
        self.IsDefeated = False
        self.Score = 0
        self.Reward=0
        self.Color=color
        self.start_time_ms = start_time_sec * 1000
        self.time_ms = self.start_time_ms
        self.Figures: set[Figure] = set()
        self.Which_Player = which_player
        self.Control=control
        self.name = name if name is not None else f"Player{which_player}"
        self.agent = None
        self.agent_path = None
                
    def startposition(self):
        self.IsDefeated = False
        self.Figures: set[Figure] = set()
        self.Score = 0
        self.time_ms=self.start_time_ms
        self.Reward=0
        
    def add_figure(self, figure):
        self.Figures.add(figure)
        
    def remove_figure(self, figure):
        self.Figures.remove(figure)
     
    def get_figure_pos_list(self):
        return [(figure.X, figure.Y) for figure in self.Figures]
    
    def empty_figures(self):
        self.Figures.clear()
    