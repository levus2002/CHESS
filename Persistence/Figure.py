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
        # promotion, Todo event küldés, promotion interface, egyenlőre fix vezér promotion
        if self.Type==Type.Pawn:
            if self.X==0 or self.X==13 or self.Y==0 or self.Y==13:
                self.Type=Type.Queen
                return
            if (self.Player==1 and self.X>=7)or (self.Player==2 and self.Y<=6) or(self.Player==3 and self.X<=6) or (self.Player==4 and self.Y>=7):
                self.Type=Type.Queen
                return


