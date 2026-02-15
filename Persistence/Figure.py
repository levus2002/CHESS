from .Type import Type
class Figure:
    def __init__(self, x, y,figure_type,player):
        self.X=x
        self.Y=y
        self.Type=figure_type
        self.Player=player
        self.HasMoved = False


