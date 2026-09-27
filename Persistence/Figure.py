from .Type import Type
class Figure:
    def __init__(self, x, y,figure_type,player):
        self.X=x
        self.Y=y
        self.Type=figure_type
        self.Player=player
        self.HasMoved = False
    
    def move(self,x,y):
        self.X=x
        self.Y=y
        self.HasMoved=True
        
    def promote(self, new_type):    
        self.Type=new_type
    
    def get_value(self):
        return Type.get_value(self.Type)
