from Model.Action import Action
from Persistence.Figure import Figure
from Persistence.Type import Type

CASTLING = {
    1: {
        "KingCastle": {
            "empty": [(0, 4), (0, 5)],
            "rook": (0, 3),
            "target": (0, 4),
            "rook_target": (0, 5),
        },
        "QueenCastle": {
            "empty": [(0, 7), (0, 8), (0, 9)],
            "rook": (0, 10),
            "target": (0, 8),
            "rook_target": (0, 7),
        },
    },
    2: {
        "KingCastle": {
            "empty": [(8, 13), (9, 13)],
            "rook": (10, 13),
            "target": (9, 13),
            "rook_target": (8, 13),
        },
        "QueenCastle": {
            "empty": [(6, 13), (5, 13), (4, 13)],
            "rook": (3, 13),
            "target": (5, 13),
            "rook_target": (6, 13),
        },
    },
    3: {
        "KingCastle": {
            "empty": [(13, 8), (13, 9)],
            "rook": (13, 10),
            "target": (13, 9),
            "rook_target": (13, 8),
        },
        "QueenCastle": {
            "empty": [(13, 6), (13, 5), (13, 4)],
            "rook": (13, 3),
            "target": (13, 5),
            "rook_target": (13, 6),
        },
    },
    4: {
        "KingCastle": {
            "empty": [(5, 0), (4, 0)],
            "rook": (3, 0),
            "target": (4, 0),
            "rook_target": (5, 0),
        },
        "QueenCastle": {
            "empty": [(7, 0), (8, 0), (9, 0)],
            "rook": (10, 0),
            "target": (8, 0),
            "rook_target": (7, 0),
        },
    },
}

PAWN_DIRECTIONS = {
    1: (1, 0),
    2: (0, -1),
    3: (-1, 0),
    4: (0, 1),
}
PROMOTION_TYPES = ("N", "B", "R", "Q")

class Movegen:
    def __init__(self, board):
        self.board = board
    
    
    def get_possible_moves(self, figure: Figure):
        match figure.Type:
            case Type.Pawn:
                return self.get_pawn_moves(figure)
            case Type.Knight:
                return self.get_knight_moves(figure)
            case Type.Bishop:
                return self.get_bishop_moves(figure)
            case Type.Rook:
                return self.get_rook_moves(figure)
            case Type.Queen:
                return self.get_queen_moves(figure)
            case Type.King:
                return self.get_king_moves(figure)
        
        return []

    def get_knight_moves(self, figure: Figure):
        if figure.Type != Type.Knight:
            raise ValueError("Figure is not a Knight")
        moves: list[Action] = []
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        
        for dx, dy in knight_moves:
            new_x = figure.X + dx
            new_y = figure.Y + dy
            
            if self.board.in_bounds(new_x, new_y):
                if self.board.is_free(new_x, new_y) or self.board.is_hit(figure.Player, new_x, new_y):
                    moves.append(Action(figure.X, figure.Y, new_x, new_y, None, None))
        return moves
    
    def get_rook_moves(self, figure: Figure) -> list[Action]:
        return self._get_sliding_moves(
            figure,
            [(1, 0), (-1, 0), (0, 1), (0, -1)]
        )

    def get_bishop_moves(self, figure: Figure) -> list[Action]:
        return self._get_sliding_moves(
            figure,
            [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        )

    def get_queen_moves(self, figure: Figure) -> list[Action]:
        return self._get_sliding_moves(
            figure,
            [
                (1, 0), (-1, 0), (0, 1), (0, -1),
                (1, 1), (1, -1), (-1, 1), (-1, -1)
            ]
        )


    def get_king_moves(self, figure: Figure) -> list[Action]:
        moves: list[Action] = []
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for dx, dy in directions:
            x = figure.X + dx
            y = figure.Y + dy

            if self.board.in_bounds(x, y):
                if (
                    self.board.is_free(x, y)
                    or self.board.is_hit(figure.Player, x, y)
                ):
                    moves.append(
                        Action(figure.X, figure.Y, x, y)
                    )

        if not figure.HasMoved:
            moves.extend(self.get_castling_moves(figure))

        return moves
        
    def get_castling_moves(self, king: Figure) -> list[Action]:
        if king.HasMoved:
            return []
        moves: list[Action] = []
        for special, config in CASTLING[king.Player].items():

            if not all(
                self.board.is_free(*pos)
                for pos in config["empty"]
            ):
                continue
            rook = self.board.get_figure(*config["rook"])
            if (
                rook is None
                or rook.Type != Type.Rook
                or rook.Player != king.Player
                or rook.HasMoved
            ):
                continue
            x, y = config["target"]
            moves.append(
                Action(
                    king.X,
                    king.Y,
                    x,
                    y,
                    special=special
                )
            )
        return moves
    
    def get_pawn_moves(self, pawn: Figure) -> list[Action]:
        moves = []
        moves.extend(self._pawn_forward_moves(pawn))
        moves.extend(self._pawn_capture_moves(pawn))
        moves.extend(self._pawn_en_passant_moves(pawn))
        return moves

    #--------------------------------------------------------------
    # Private helper methods
    #--------------------------------------------------------------
    
    def _get_sliding_moves(self,figure: Figure, directions: list[tuple[int, int]]) -> list[Action]:
            moves: list[Action] = []
            for dx, dy in directions:
                x, y = figure.X, figure.Y
                while True:
                    x += dx
                    y += dy

                    if not self.board.in_bounds(x, y):
                        break

                    if self.board.is_free(x, y):
                        moves.append(
                            Action(figure.X, figure.Y, x, y)
                        )

                    elif self.board.is_hit(figure.Player, x, y):
                        moves.append(
                            Action(figure.X, figure.Y, x, y)
                        )
                        break

                    else:
                        break

            return moves
    
    
    
    def _pawn_forward_moves(self, pawn: Figure) -> list[Action]:
        moves = []
        dx, dy = PAWN_DIRECTIONS[pawn.Player]
        x = pawn.X + dx
        y = pawn.Y + dy
        if not self.board.in_bounds(x, y):
            return moves
        if not self.board.is_free(x, y):
            return moves
        moves.extend(self._pawn_actions(pawn, x, y))
        if not pawn.HasMoved:
            x2 = pawn.X + 2 * dx
            y2 = pawn.Y + 2 * dy
            if (
                self.board.in_bounds(x2, y2)
                and self.board.is_free(x2, y2)
            ):
                moves.append(
                    Action(
                        pawn.X, pawn.Y,
                        x2, y2,
                        special="double"
                    )
                )
        return moves
    
    def _pawn_capture_moves(self, pawn: Figure) -> list[Action]:
        moves = []
        for dx, dy in self._pawn_capture_directions(pawn.Player):
            x = pawn.X + dx
            y = pawn.Y + dy
            if not self.board.in_bounds(x, y):
                continue
            if self.board.is_hit(pawn.Player, x, y):
                moves.extend(self._pawn_actions(pawn, x, y))
        return moves

    def _pawn_capture_directions(self, player_id: int):
        dx, dy = PAWN_DIRECTIONS[player_id]

        return [
            (dx + dy, dy - dx),
            (dx - dy, dy + dx),
        ]
    
    def _is_promotion_square(self, row: int, col: int, player_id: int) -> bool:
        if row in (0, 13) or col in (0, 13):
            return True
        return (
            (player_id == 1 and row >= 7)
            or (player_id == 2 and col <= 6)
            or (player_id == 3 and row <= 6)
            or (player_id == 4 and col >= 7)
        )
    


    def _pawn_actions(self, pawn: Figure, row: int, col: int, special=None ) -> list[Action]:
        if self._is_promotion_square(row, col, pawn.Player):
            return [
                Action(
                    pawn.X, pawn.Y,
                    row, col,
                    special=special,
                    promotion=piece
                )
                for piece in PROMOTION_TYPES
            ]

        return [
            Action(
                pawn.X, pawn.Y,
                row, col,
                special=special
            )
        ]
    
    def _pawn_en_passant_moves(self, pawn: Figure) -> list[Action]:
        moves: list[Action] = []
        for cx, cy in self._pawn_capture_directions(pawn.Player):
            x = pawn.X + cx
            y = pawn.Y + cy

            if not self.board.in_bounds(x, y):
                continue
            # En passant destination must be empty. Otherwise we could take multiple pieces in one move.
            if not self.board.is_free(x, y):
                continue
            owner = self.board.en_passants.get((x, y))
            if owner is None or owner == pawn.Player:
                continue

            owner_dx, owner_dy = PAWN_DIRECTIONS[owner]
            captured_x = x + owner_dx
            captured_y = y + owner_dy

            if not self.board.in_bounds(captured_x, captured_y):
                continue
            captured = self.board.get_figure(captured_x, captured_y)
            if (
                captured is None
                or captured.Type != Type.Pawn
                or captured.Player != owner
            ):
                continue

            moves.extend(
                self._pawn_actions(
                    pawn, x, y,
                    special="en_passant"
                )
            )
        return moves
    
    def get_all_moves(self, figures) -> list[Action]:
        actions = []

        for figure in figures:
            actions.extend(self.get_possible_moves(figure))

        return actions