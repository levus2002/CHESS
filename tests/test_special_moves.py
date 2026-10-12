
import unittest

from Model.Dataclasses import Action
from Model.GameModel import GameModel
from Model.Movegen import CASTLING, PAWN_DIRECTIONS, PROMOTION_TYPES
from Persistence.Board import Board
from Persistence.Figure import Figure
from Persistence.Player import Player
from Persistence.Type import Type


class TestSpecialMoves(unittest.TestCase):

    def setUp(self):
        self.players = {pid: Player(pid) for pid in range(1, 5)}
        self.game = GameModel(Board(), self.players)
        self.board = self.game.board

    def add_piece(self, row, col, player=1,
                  piece_type=Type.Pawn, moved=False):
        piece = Figure(row, col, piece_type, player)
        piece.HasMoved = moved
        self.game.add_figure(piece)
        return piece

    def assert_piece_at(self, piece, row, col):
        self.assertIs(self.board.get_figure(row, col), piece)
        self.assertEqual((piece.X, piece.Y), (row, col))

    def assert_action_recorded(self, action, player):
        self.assertEqual(self.game.action_history, [action])
        self.assertEqual(
            self.game.current_player,
            player % 4 + 1,
        )

    # --------------------------------------------------
    # Castling
    # --------------------------------------------------

    def test_castling_all_players_and_sides(self):
        rook_positions = {
            1: (3, 5),
            2: (5, 10),
            3: (10, 8),
            4: (8, 3),
        }
        for player in range(1, 5):
            for side in ("KingCastle", "QueenCastle"):
                with self.subTest(player=player, side=side):
                    self.setUp()
                    for other_player, position in rook_positions.items():
                        if other_player != player:
                            self.add_piece(
                                *position,
                                player=other_player,
                                piece_type=Type.Rook
                            )
                    config = CASTLING[player][side]
                    start = CASTLING[player]["king_start"]

                    king = self.add_piece(
                        *start, player=player,
                        piece_type=Type.King,
                    )
                    rook = self.add_piece(
                        *config["rook"], player=player,
                        piece_type=Type.Rook,
                    )

                    self.game.current_player = player
                    action = Action(
                        *start, *config["target"], special=side
                    )

                    self.game.step(action)

                    self.assertIsNone(self.board.get_figure(*start))
                    self.assertIsNone(
                        self.board.get_figure(*config["rook"])
                    )

                    self.assert_piece_at(king, *config["target"])
                    self.assert_piece_at(
                        rook, *config["rook_target"]
                    )

                    self.assertTrue(king.HasMoved)
                    self.assertTrue(rook.HasMoved)

                    self.assertIn(king, self.players[player].Figures)
                    self.assertIn(rook, self.players[player].Figures)
                    self.assert_action_recorded(action, player)

    def test_castling_cannot_be_repeated(self):
        config = CASTLING[1]["KingCastle"]
        start = CASTLING[1]["king_start"]

        king = self.add_piece(
            *start, piece_type=Type.King
        )
        self.add_piece(
            *config["rook"], piece_type=Type.Rook
        )

        self.game.step(
            Action(*start, *config["target"], special="KingCastle")
        )

        self.assertFalse(
            any(
                action.special in ("KingCastle", "QueenCastle")
                for action in self.game.movegen.get_possible_moves(king)
            )
        )

    # --------------------------------------------------
    # Promotion
    # --------------------------------------------------

    def test_promotion_all_players_and_types(self):
        starts = {
            1: (6, 6),
            2: (6, 7),
            3: (7, 6),
            4: (6, 6),
        }

        types = {
            "N": Type.Knight,
            "B": Type.Bishop,
            "R": Type.Rook,
            "Q": Type.Queen,
        }
        
        rook_positions = {
            1: (3, 5),
            2: (5, 10),
            3: (10, 8),
            4: (8, 3),
        }

        for player, start in starts.items():
            for promotion in PROMOTION_TYPES:
                with self.subTest(
                    player=player, promotion=promotion
                ):
                    self.setUp()
                    for other_player, position in rook_positions.items():
                        if other_player != player:
                            self.add_piece(
                                *position,
                                player=other_player,
                                piece_type=Type.Rook
                            )
                    

                    pawn = self.add_piece(
                        *start, player=player, moved=True
                    )
                    dr, dc = PAWN_DIRECTIONS[player]
                    target = (
                        start[0] + dr,
                        start[1] + dc,
                    )

                    self.game.current_player = player
                    action = Action(
                        *start, *target, promotion=promotion
                    )

                    self.game.step(action)

                    self.assertIsNone(self.board.get_figure(*start))
                    self.assert_piece_at(pawn, *target)
                    self.assertEqual(pawn.Type, types[promotion])
                    self.assertTrue(pawn.HasMoved)
                    self.assertIn(
                        pawn, self.players[player].Figures
                    )
                    self.assert_action_recorded(action, player)

    def test_promotion_on_capture(self):
        self.add_piece(10, 9, player=2, piece_type=Type.Rook)
        pawn = self.add_piece(
            6, 6, player=1, moved=True
        )
        victim = self.add_piece(
            7, 7, player=2, piece_type=Type.Rook
        )

        action = Action(6, 6, 7, 7, promotion="Q")
        self.game.step(action)

        self.assert_piece_at(pawn, 7, 7)
        self.assertEqual(pawn.Type, Type.Queen)
        self.assertNotIn(victim, self.players[2].Figures)
        self.assertEqual(
            self.players[1].Score, victim.get_value()
        )
        self.assert_action_recorded(action, 1)

    def test_promotion_requires_explicit_choice(self):
        pawn = self.add_piece(
            6, 6, player=1, moved=True
        )

        with self.assertRaises(ValueError):
            self.game.step(Action(6, 6, 7, 6))

        self.assert_piece_at(pawn, 6, 6)
        self.assertEqual(pawn.Type, Type.Pawn)
        self.assertEqual(self.game.action_history, [])

    # --------------------------------------------------
    # Double moves and en passant registration
    # --------------------------------------------------

    def test_double_move_registers_en_passant_all_players(self):
        starts = {
            1: (1, 6),
            2: (6, 12),
            3: (12, 6),
            4: (6, 1),
        }
        rook_positions = {
            1: (3, 5),
            2: (5, 10),
            3: (10, 8),
            4: (8, 3),
        }
        for player, start in starts.items():
            with self.subTest(player=player):
                self.setUp()
                for other_player, position in rook_positions.items():
                    if other_player != player:
                        self.add_piece(
                            *position,
                            player=other_player,
                            piece_type=Type.Rook
                        )
                pawn = self.add_piece(*start, player=player)
                dr, dc = PAWN_DIRECTIONS[player]

                passed = (
                    start[0] + dr,
                    start[1] + dc,
                )
                target = (
                    start[0] + 2 * dr,
                    start[1] + 2 * dc,
                )

                self.game.current_player = player
                action = Action(
                    *start, *target, special="double"
                )

                self.game.step(action)

                self.assert_piece_at(pawn, *target)
                self.assertEqual(
                    self.board.en_passants, {passed: player}
                )
                self.assert_action_recorded(action, player)

    # --------------------------------------------------
    # En passant capture
    # --------------------------------------------------

    def test_en_passant_capture_all_players(self):
        starts = {
            1: (4, 6),
            2: (6, 9),
            3: (9, 6),
            4: (6, 4),
        }
        rook_positions = {
            1: (3, 5),
            2: (5, 10),
            3: (10, 8),
            4: (8, 3),
        }

        for player, start in starts.items():
            with self.subTest(player=player):
                self.setUp()
                for other_player, position in rook_positions.items():
                    if other_player != player:
                        self.add_piece(
                            *position,
                            player=other_player,
                            piece_type=Type.Rook
                        )
                owner = player % 4 + 1
                dr, dc = PAWN_DIRECTIONS[player]
                owner_dr, owner_dc = PAWN_DIRECTIONS[owner]

                target = (
                    start[0] + dr + dc,
                    start[1] + dc - dr,
                )
                captured_pos = (
                    target[0] + owner_dr,
                    target[1] + owner_dc,
                )

                pawn = self.add_piece(
                    *start, player=player, moved=True
                )
                victim = self.add_piece(
                    *captured_pos, player=owner,
                    moved=True,
                )
                self.board.en_passants[target] = owner

                self.game.current_player = player
                action = Action(
                    *start, *target, special="en_passant"
                )

                self.game.step(action)

                self.assertIsNone(self.board.get_figure(*start))
                self.assertIsNone(
                    self.board.get_figure(*captured_pos)
                )
                self.assert_piece_at(pawn, *target)

                self.assertNotIn(
                    victim, self.players[owner].Figures
                )
                self.assertEqual(
                    self.players[player].Score,
                    victim.get_value(),
                )
                self.assert_action_recorded(action, player)

    def test_en_passant_entry_expires_on_owners_next_turn(self):
        pawn = self.add_piece(1, 6, player=1)
        self.add_piece(
            5, 10, player=2, piece_type=Type.Knight
        )
        self.add_piece(
            8, 8, player=3, piece_type=Type.Knight
        )
        self.add_piece(
            6, 3, player=4, piece_type=Type.Knight
        )

        self.game.step(
            Action(1, 6, 3, 6, special="double")
        )

        passed = (2, 6)
        self.assert_piece_at(pawn, 3, 6)
        self.assertEqual(self.board.en_passants.get(passed), 1)

        moves = (
            (Action(5, 10, 7, 11), 3),
            (Action(8, 8, 10, 9), 4),
            (Action(6, 3, 8, 4), 1),
        )

        for action, next_player in moves:
            with self.subTest(next_player=next_player):
                self.game.step(action)
                self.assertEqual(
                    self.game.current_player, next_player
                )

                if next_player == 1:
                    self.assertNotIn(
                        passed, self.board.en_passants
                    )
                else:
                    self.assertEqual(
                        self.board.en_passants.get(passed), 1
                    )

    def test_en_passant_capture_with_promotion(self):
        self.add_piece(10, 9, player=2, piece_type=Type.Rook)
        pawn = self.add_piece(
            6, 6, player=1, moved=True
        )
        victim = self.add_piece(
            7, 6, player=2, moved=True
        )

        self.board.en_passants[(7, 7)] = 2

        action = Action(
            6, 6, 7, 7,
            special="en_passant",
            promotion="Q",
        )

        self.game.step(action)

        self.assert_piece_at(pawn, 7, 7)
        self.assertEqual(pawn.Type, Type.Queen)
        self.assertIsNone(self.board.get_figure(7, 6))
        self.assertNotIn(victim, self.players[2].Figures)
        self.assertEqual(
            self.players[1].Score, victim.get_value()
        )
        self.assert_action_recorded(action, 1)























if __name__ == "__main__":
    unittest.main()
