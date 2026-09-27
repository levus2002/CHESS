from Persistence.Figure import Figure

#Functions
#in_bounds(row,col) or in_bounds((row,col)) -> bool         
#is_hit(playerid,row,col) or is_hit(playerid,(row,col)) -> bool
#is_friendly(playerid,row,col) or is_friendly(playerid,(row,col)) -> bool
#is_free(row,col) or is_free((row,col)) -> bool

class Board():
    def __init__(self):
        self.move_number = 1
        self.figure_board: list[list[Figure | None]] = [[None] * 14 for _ in range(14)]
        self.en_passants: dict[tuple[int, int], int] = {}
        

    def empty_board(self):
        return [
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
    [-1, -1, -1, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1]]
    
    def in_bounds(self, *args):
        match args:
            case (row, col) | ((row, col),):
                return (
                    0 <= row < 14
                    and 0 <= col < 14
                    and self.empty_board()[row][col] != -1
                )
            case _:
                raise TypeError("Expected (row, col) or ((row, col),)")
            
    def is_hit(self,playerid, *args):
        match args:
            case (row, col) | ((row, col),):
                return (
                    self.in_bounds(row, col)
                    and self.figure_board[row][col] is not None
                    and self.figure_board[row][col].Player != playerid
                )
            case _:
                raise TypeError("Expected (row, col) or ((row, col),)")
    
    def is_friendly(self,playerid, *args):
            match args:
                case (row, col) | ((row, col),):
                    return (
                        self.in_bounds(row, col)
                        and self.figure_board[row][col] is not None
                        and self.figure_board[row][col].Player == playerid
                    )
                case _:
                    raise TypeError("Expected (row, col) or ((row, col),)")
    
    def is_free(self, *args):
            match args:
                case (row, col) | ((row, col),):
                    return (
                        self.in_bounds(row, col)
                        and self.figure_board[row][col] is None
                    )
                case _:
                    raise TypeError("Expected (row, col) or ((row, col),)")
                
    def place_figure(self, figure: Figure, *args):
        match args:
            case (row, col) | ((row, col),):
                if self.in_bounds(row, col):
                    if self.figure_board[row][col] is None:
                        self.figure_board[row][col] = figure
                    else:
                        raise ValueError("Position already occupied by another figure")
                else:
                    raise ValueError("Figure position out of bounds")
            case _:
                raise TypeError("Expected (row, col) or ((row, col),)")

    def remove_figure(self, *args):
        match args:
            case (row, col) | ((row, col),):
                if self.in_bounds(row, col):
                    figure=self.figure_board[row][col]
                    if figure is not None:
                        self.figure_board[row][col] = None
                        return figure
                    else:
                        raise ValueError("No figure at the specified position")
                else:
                    raise ValueError("Position out of bounds")
            case _:
                raise TypeError("Expected (row, col) or ((row, col),)")
    
    def replace_figure(self, figure: Figure, *args):
        match args:
            case (row, col) | ((row, col),):
                if self.in_bounds(row, col):
                    self.remove_figure(row, col)
                    self.figure_board[row][col] = figure
                else:
                    raise ValueError("Figure position out of bounds")
            case _:
                raise TypeError("Expected (row, col) or ((row, col),)")
    
    def get_figure(self, *args):
        match args:
            case (row, col) | ((row, col),):
                if self.in_bounds(row, col):
                    return self.figure_board[row][col]
                else:
                    raise ValueError("Position out of bounds")
            case _:
                raise TypeError("Expected (row, col) or ((row, col),)")

    def clear_en_passants(self, player_id: int):
        to_remove = [
            pos for pos, pid in self.en_passants.items() if pid == player_id
        ]
        for pos in to_remove:
            del self.en_passants[pos]
    
    
        
    
    