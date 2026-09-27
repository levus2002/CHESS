from Model.Action import Action
from Model.Movegen import CASTLING, PAWN_DIRECTIONS, Movegen
from Persistence.Figure import Figure
from Persistence.Player import Player
from Persistence.Type import Type
from Persistence.Board import Board






class GameModel:
    def __init__(self, board: Board, players: dict[int, Player]):
        self.isgameover = False
        self.move_number = 1
        self.action_history: list[Action] = []
        self.board = board
        self.players = players
        self.movegen = Movegen(board)
        self.selected_figure: Figure | None = None
        self.current_actions: list[Action] = []
        self.action_lookup: dict[tuple[int, int], list[Action]] = {}
        self.current_player: int = 1
    
    def CurrentPlayer(self):
        return self.players[self.current_player]
    
    def get_player(self, player_id: int) -> Player:
        return self.players[player_id]
    
    def get_player_from_pos(self, *args) -> Player | None:
        match args:
            case (row, col) | ((row, col),):
                figure = self.board.get_figure(row, col)
                if figure:
                    return self.players[figure.Player]
                else:
                    return None
        raise TypeError("Expected (row, col) or ((row, col),)")
    
    def add_figure(self, figure: Figure):
        player = self.players[figure.Player]
        self.board.place_figure(figure, figure.X, figure.Y)
        player.add_figure(figure)


    #--------------------------------------------------
    # Game Start and Reset
    #--------------------------------------------------
    def new_game(self):
        self.isgameover = False
        self.current_player = 1
        self.move_number = 1
        self.clear_selection()
        self.action_history: list[Action] = []
        
        self.board.figure_board = [[None] * 14 for _ in range(14)]
        self.board.en_passants = {}
        for player in self.players.values():
            player.startposition()
        self.setup_players()
        
    def setup_players(self):
        self.setup_player1()
        self.setup_player2()
        self.setup_player3()
        self.setup_player4()

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
            self.add_figure(Figure(i+3, 12, Type.Pawn, 2))
        self.add_figure(Figure(3, 13, Type.Rook, 2))
        self.add_figure(Figure(10, 13, Type.Rook, 2))
        self.add_figure(Figure(4, 13, Type.Knight, 2))
        self.add_figure(Figure(9, 13, Type.Knight, 2))
        self.add_figure(Figure(5, 13, Type.Bishop, 2))
        self.add_figure(Figure(8, 13, Type.Bishop, 2))
        self.add_figure(Figure(6, 13, Type.Queen, 2))
        self.add_figure(Figure(7, 13, Type.King, 2))

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
            self.add_figure(Figure(i+3, 1, Type.Pawn, 4))
        self.add_figure(Figure(3, 0, Type.Rook, 4))
        self.add_figure(Figure(10, 0, Type.Rook, 4))
        self.add_figure(Figure(4, 0, Type.Knight, 4))
        self.add_figure(Figure(9, 0, Type.Knight, 4))
        self.add_figure(Figure(5, 0, Type.Bishop, 4))
        self.add_figure(Figure(8, 0, Type.Bishop, 4))
        self.add_figure(Figure(6, 0, Type.King, 4))
        self.add_figure(Figure(7, 0, Type.Queen, 4))
        
        
    #--------------------------------------------------
    # Game Logic
    #--------------------------------------------------
        
    def clear_selection(self):
        self.selected_figure = None
        self.current_actions = []
        self.action_lookup = {}
    
    def select_figure(self, row: int, col: int) -> list[list[int]]:
        figure = self.board.get_figure(row, col)

        if figure is None or figure.Player != self.current_player:
            return [[0] * 14 for _ in range(14)]

        self.selected_figure = figure
        self.current_actions = self.movegen.get_possible_moves(figure)
        self.action_lookup = {}

        highlights = [[0] * 14 for _ in range(14)]

        for action in self.current_actions:
            target = (action.to_row, action.to_col)

            self.action_lookup.setdefault(target, []).append(action)

            if self.board.is_friendly(self.current_player, action.to_row, action.to_col):
                raise ValueError("Cannot move to a square occupied by a friendly piece.")
            if action.promotion is not None:
                highlight = 3

            elif (
                action.special == "en_passant"
                or self.board.is_hit(self.current_player, action.to_row, action.to_col)
            ):
                highlight = 2
            else:
                highlight = 1
                
            highlights[action.to_row][action.to_col] = highlight

        return highlights
    
    def step(self, action: Action):
        figure = self._validate_action(action)
        self._execute_action(figure, action)
        self._advance_turn()
        
        
        
        
    #--------------------------------------------------
    # Private helper methods
    #--------------------------------------------------
        
    def _validate_action(self, action: Action) -> Figure:
        figure = self.board.get_figure(
            action.from_row, action.from_col
        )
        if figure is None:
            raise ValueError("No figure at source square")
        if figure.Player != self.current_player:
            raise ValueError("Not this player's turn")
        if action not in self.movegen.get_possible_moves(figure):
            raise ValueError("Invalid action")
        return figure
    


    def _advance_turn(self):
        old_player = self.current_player
        self.current_player = self._next_active_player()
        if old_player > self.current_player:
            self.move_number += 1
        self.board.clear_en_passants(self.current_player)

    def _move_figure(
        self,
        figure: Figure,
        row: int,
        col: int
    ):
        self.board.remove_figure(figure.X, figure.Y)
        figure.X = row
        figure.Y = col
        figure.HasMoved = True
        self.board.place_figure(figure, row, col)
    
    def _next_active_player(self) -> int:
        for offset in range(1, 5):
            player_id = (self.current_player - 1 + offset) % 4 + 1

            if not self.players[player_id].IsDefeated:
                if player_id == self.current_player:
                    self.isgameover = True

                return player_id
        raise RuntimeError("No active players remaining")
    
    def _execute_action(self, figure: Figure, action: Action):
        captured = self._get_captured_figure(action)
        if captured is not None:
            self._capture_figure(captured)
        self._move_figure(
            figure,
            action.to_row,
            action.to_col
        )
        if action.special in ("KingCastle", "QueenCastle"):
            self._execute_castling(figure, action)

        if action.promotion is not None:
            self._promote_figure(figure, action.promotion)

        if action.special == "double":
            self._register_en_passant(figure, action)
        self.action_history.append(action)
        
    
    def _get_captured_figure(self, action: Action) -> Figure | None:
        if action.special == "en_passant":
            owner = self.board.en_passants.get(
                (action.to_row, action.to_col)
            )

            if owner is None:
                raise ValueError("No en passant entry at destination")

            dx, dy = PAWN_DIRECTIONS[owner]

            captured_row = action.to_row + dx
            captured_col = action.to_col + dy
            return self.board.get_figure(captured_row, captured_col)
        return self.board.get_figure(action.to_row, action.to_col)
    
    def _capture_figure(self, figure: Figure):
        self.board.remove_figure(figure.X, figure.Y)
        player = self.players[figure.Player]
        player.remove_figure(figure)
        self.CurrentPlayer().Score += figure.get_value()
        if figure.Type == Type.King:
            player.IsDefeated = True
    
    def _execute_castling(self, king: Figure, action: Action):
        if action.special not in ("KingCastle", "QueenCastle"):
            raise ValueError("Invalid castling action")
        config = CASTLING[king.Player][action.special]

        rook = self.board.get_figure(*config["rook"])
        if rook is None:
            raise RuntimeError("Castling rook is missing")
        self._move_figure(rook, *config["rook_target"])
    
    def _promote_figure(self, figure: Figure, new_type: str):
        if figure.Type != Type.Pawn:
            raise ValueError("Only pawns can be promoted")

        for piece_type in (
            Type.Queen, Type.Rook, Type.Bishop, Type.Knight
        ):
            if piece_type.char == new_type:
                figure.promote(piece_type)
                return
        raise ValueError("Invalid promotion type")
    
    def _register_en_passant(self, pawn: Figure, action: Action):
        if pawn.Type != Type.Pawn:
            raise ValueError("Only pawns can register en passant")
        passed_row = (action.from_row + action.to_row) // 2
        passed_col = (action.from_col + action.to_col) // 2
        self.board.en_passants[(passed_row, passed_col)] = pawn.Player

















































































