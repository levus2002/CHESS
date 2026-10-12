import unittest

from Model.Dataclasses import Action
from Model.Movegen import CASTLING, PAWN_DIRECTIONS, Movegen, PROMOTION_TYPES
from Persistence.Board import Board
from Persistence.Type import Type
from Persistence.Figure import Figure




class TestMovegen(unittest.TestCase):
    def setUp(self):
        self.board = Board()
        self.movegen = Movegen(self.board)

    def add_piece(self, row, col, player=1, piece_type=Type.Pawn, moved=False):
        piece = Figure(row, col, piece_type, player)
        piece.HasMoved = moved
        self.board.place_figure(piece, row, col)
        return piece


    def destinations(self,actions):
        return {(a.to_row, a.to_col) for a in actions}


    def moves(self, piece):
        return self.movegen.get_possible_moves(piece)

    def assert_targets(self, piece, expected):
        self.assertEqual(self.destinations(self.moves(piece)), set(expected))
        
        
        
    #------------------------------------------------------
    #       Pawn Tests
    #
    # test_pawn_double_move
    # test_pawn_initial_moves_all_players
    # test_pawn_forward_blocking
    # test_pawn_capture_directions_all_players
    # test_promotion_all_players_and_types
    # test_promotion_on_any_outer_edge
    # test_en_passant_generation_all_players
    # test_en_passant_requires_matching_pawn_and_empty_target
    #------------------------------------------------
        
    def test_pawn_double_move(self):
        pawn = self.add_piece(1, 8)
        self.assertEqual(set(self.moves(pawn)), {
            Action(1, 8, 2, 8), Action(1, 8, 3, 8, special="double")
        })
        self.board.remove_figure(1, 8)
        pawn.move(3, 8)
        self.board.place_figure(pawn, 3, 8)
        self.assertEqual(self.moves(pawn), [Action(3, 8, 4, 8)])
        
    def test_pawn_initial_moves_all_players(self):
        starts = {1: (1, 6), 2: (6, 12), 3: (12, 6), 4: (6, 1)}
        for player, (row, col) in starts.items():
            with self.subTest(player=player):
                self.setUp()
                movegen = Movegen(self.board)
                pawn = self.add_piece(row, col, player)
                dr, dc = PAWN_DIRECTIONS[player]
                self.assertEqual(set(movegen.get_possible_moves(pawn)), {
                    Action(row, col, row + dr, col + dc),
                    Action(row, col, row + 2 * dr, col + 2 * dc, special="double"),
                })

    def test_pawn_forward_blocking(self):
        for blocker_distance in (1, 2):
            with self.subTest(blocker_distance=blocker_distance):
                self.setUp()
                pawn = self.add_piece( 1, 6)
                self.add_piece( 1 + blocker_distance, 6, 2)
                expected = [] if blocker_distance == 1 else [Action(1, 6, 2, 6)]
                self.assertEqual(self.moves(pawn), expected)

    def test_pawn_capture_directions_all_players(self):
        starts = {1: (4, 6), 2: (6, 9), 3: (9, 6), 4: (6, 4)}
        for player, (row, col) in starts.items():
            with self.subTest(player=player):
                self.setUp()
                pawn = self.add_piece( row, col, player, moved=True)
                dr, dc = PAWN_DIRECTIONS[player]
                capture_offsets = [(dr + dc, dc - dr), (dr - dc, dc + dr)]
                expected = set()
                for i, (dx, dy) in enumerate(capture_offsets):
                    target = (row + dx, col + dy)
                    self.add_piece( *target, player=(player % 4) + 1 if i == 0 else player)
                    if i == 0:
                        expected.add(target)
                expected.add((row + dr, col + dc))
                self.assertEqual(self.destinations(self.moves(pawn)), expected)

    def test_promotion_all_players_and_types(self):
        starts = {1: (6, 6), 2: (6, 7), 3: (7, 6), 4: (6, 6)}
        for player, (row, col) in starts.items():
            with self.subTest(player=player):
                self.setUp()
                pawn = self.add_piece( row, col, player, moved=True)
                dr, dc = PAWN_DIRECTIONS[player]
                target = (row + dr, col + dc)
                actions = self.moves(pawn)
                self.assertEqual(set(actions), {
                    Action(row, col, *target, promotion=kind)
                    for kind in PROMOTION_TYPES
                })

    def test_promotion_on_any_outer_edge(self):
        self.setUp()
        pawn = self.add_piece( 3, 12, player=1, moved=True)
        self.add_piece( 4, 13, player=2)
        actions = self.moves(pawn)
        promotions = [a for a in actions if (a.to_row, a.to_col) == (4, 13)]
        self.assertEqual({a.promotion for a in promotions}, set(PROMOTION_TYPES))

    def test_en_passant_generation_all_players(self):
        for player in range(1, 5):
            with self.subTest(player=player):
                self.setUp()
                row, col = 6, 6
                pawn = self.add_piece( row, col, player, moved=True)
                dr, dc = PAWN_DIRECTIONS[player]
                target = (row + dr + dc, col + dc - dr)
                owner = player % 4 + 1
                owner_dr, owner_dc = PAWN_DIRECTIONS[owner]
                captured = (target[0] + owner_dr, target[1] + owner_dc)
                self.add_piece( *captured, player=owner)
                self.board.en_passants[target] = owner
                actions = self.moves(pawn)
                self.assertEqual(
                    {a.promotion for a in actions if a.special == "en_passant"
                     and (a.to_row, a.to_col) == target},
                    set(PROMOTION_TYPES),
                )

    def test_en_passant_requires_matching_pawn_and_empty_target(self):
        for case in ("no_entry", "wrong_owner", "missing_pawn", "wrong_piece", "occupied_target"):
            with self.subTest(case=case):
                self.setUp()
                pawn = self.add_piece( 4, 6, moved=True)
                target = (5, 7)
                if case != "no_entry":
                    self.board.en_passants[target] = 1 if case == "wrong_owner" else 2
                if case not in ("missing_pawn", "no_entry"):
                    self.add_piece( 5, 6, player=2,
                              piece_type=Type.Rook if case == "wrong_piece" else Type.Pawn)
                if case == "occupied_target":
                    self.add_piece( *target, player=2)
                self.assertFalse(any(a.special == "en_passant"
                                     for a in self.moves(pawn)))    
        
        
        
        
        
        
        
        
        
        
        
        

    def test_knight(self):
        knight = self.add_piece(3, 3, piece_type=Type.Knight)
        self.add_piece(1, 4)
        self.add_piece(4, 5, 2)
        self.assert_targets(knight, {(5, 4), (5, 2), (2, 5), (4, 5), (4, 1)})
        self.assertNotIn((2, 1), self.destinations(self.moves(knight)))
        self.assertNotIn((1, 2), self.destinations(self.moves(knight)))

    def test_bishop(self):
        bishop = self.add_piece(5, 5, piece_type=Type.Bishop)
        self.add_piece(8, 2)
        self.add_piece(1, 9, 2)
        targets = self.destinations(self.moves(bishop))
        self.assertEqual(len(targets), 13)
        self.assertTrue({(7, 3), (3, 3), (2, 8), (1, 9), (10, 10)} <= targets)
        self.assertTrue({(8, 2), (2, 2), (0, 10), (11, 11)}.isdisjoint(targets))

    def test_rook(self):
        rook = self.add_piece(7, 2, piece_type=Type.Rook)
        self.add_piece(7, 10)
        self.add_piece(9, 2, 2)
        targets = self.destinations(self.moves(rook))
        self.assertEqual(len(targets), 15)
        self.assertTrue({(7, 9), (3, 2), (7, 0), (9, 2)} <= targets)
        self.assertTrue({(7, 10), (7, 13), (2, 2), (7, -1), (10, 2)}.isdisjoint(targets))

    def test_queen(self):
        queen = self.add_piece(4, 2, piece_type=Type.Queen)
        self.add_piece(6, 4)
        self.add_piece(7, 2, 2)
        self.add_piece(4, 8, 3, Type.Bishop)
        targets = self.destinations(self.moves(queen))
        self.assertEqual(len(targets), 20)
        self.assertTrue({(3, 1), (3, 2), (4, 1), (4, 0), (0, 6),
                         (5, 3), (7, 2), (4, 8)} <= targets)
        self.assertTrue({(6, 4), (8, 2), (4, 9)}.isdisjoint(targets))

    def test_king(self):
        king = self.add_piece(3, 3, piece_type=Type.King)
        self.add_piece(4, 4)
        self.add_piece(4, 2, 2)
        self.add_piece(2, 4, 3, Type.Bishop)
        self.assert_targets(king, {(3, 2), (2, 3), (2, 4),
                                   (3, 4), (4, 2), (4, 3)})

    def test_get_all_moves(self):
        queen = self.add_piece(3, 10, piece_type=Type.Queen)
        rook = self.add_piece(6, 6, piece_type=Type.Rook)
        self.assertEqual(len(self.moves(queen)), 39)
        self.assertEqual(len(self.moves(rook)), 26)
        self.assertEqual(set(self.movegen.get_all_moves([queen, rook])),
                         set(self.moves(queen) + self.moves(rook)))



    def test_castling_all_players_and_sides(self):
        starts = {1: (0, 6), 2: (7, 13), 3: (13, 7), 4: (6, 0)}
        for player, start in starts.items():
            for side in ("KingCastle", "QueenCastle"):
                config = CASTLING[player][side]
                with self.subTest(player=player, side=side):
                    self.setUp()
                    king = self.add_piece( *start, player=player, piece_type=Type.King)
                    self.add_piece( *config["rook"], player=player, piece_type=Type.Rook)
                    self.assertIn(Action(*start, *config["target"], special=side),
                                  self.moves(king))

    def test_castling_restrictions(self):
        start = (0, 6)
        config = CASTLING[1]["KingCastle"]
        for condition in ("king_moved", "rook_moved", "rook_missing",
                          "wrong_rook_type", "enemy_rook", "blocked"):
            with self.subTest(condition=condition):
                self.setUp()
                king = self.add_piece( *start, piece_type=Type.King,
                                 moved=condition == "king_moved")
                if condition != "rook_missing":
                    self.add_piece( *config["rook"],
                              player=2 if condition == "enemy_rook" else 1,
                              piece_type=Type.Bishop if condition == "wrong_rook_type" else Type.Rook,
                              moved=condition == "rook_moved")
                if condition == "blocked":
                    self.add_piece( *config["empty"][0])
                self.assertFalse(any(a.special == "KingCastle"
                                     for a in self.moves(king)))

    def test_castling_requires_king_start_square(self):
        self.setUp()
        king = self.add_piece( 0, 5, piece_type=Type.King)
        self.add_piece( 0, 10, piece_type=Type.Rook)
        self.assertFalse(any(a.special == "QueenCastle"
                             for a in self.moves(king)))













if __name__ == "__main__":
    unittest.main()
