from enum import Enum
class Type(Enum):
    Pawn = (1, "P")
    Knight = (2, "N")
    Bishop = (3, "B")
    Rook = (5, "R")
    Queen = (9, "Q")
    King = (10, "K")

    def __init__(self, value, char):
        self._value_ = value
        self.char = char