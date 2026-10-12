
import unittest

from Model.Dataclasses import Action
from Model.GameModel import GameModel
from Persistence.Board import Board
from Persistence.Figure import Figure
from Persistence.Player import Player
from Persistence.Type import Type


class TestGameModel(unittest.TestCase):

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

    def assert_no_piece_at(self, row, col):
        self.assertIsNone(self.board.get_figure(row, col))

    # --------------------------------------------------
    # Movement and captures
    # --------------------------------------------------

    def test_basic_move(self):
        pawn = self.add_piece(1, 6)

        self.add_piece(10, 5, player=2, piece_type=Type.Rook)
        self.add_piece(10, 9, player=3, piece_type=Type.Rook)
        self.game.step(Action(1, 6, 2, 6))

        self.assert_no_piece_at(1, 6)
        self.assert_piece_at(pawn, 2, 6)
        self.assertTrue(pawn.HasMoved)
        self.assertIn(pawn, self.players[1].Figures)
        self.assertEqual(self.game.current_player, 2)

    def test_capture_updates_board_figures_and_score(self):
        rook = self.add_piece(5, 5, piece_type=Type.Rook)
        victim = self.add_piece(5, 7, player=2,
                                piece_type=Type.Knight)

        self.game.step(Action(5, 5, 5, 7))

        self.assert_no_piece_at(5, 5)
        self.assert_piece_at(rook, 5, 7)
        self.assertNotIn(victim, self.players[2].Figures)
        self.assertIn(rook, self.players[1].Figures)
        self.assertEqual(self.players[1].Score, victim.get_value())
        self.assertEqual(self.players[2].Score, 0)

    def test_capture_king_defeats_player(self):
        rook = self.add_piece(5, 5, piece_type=Type.Rook)
        king = self.add_piece(5, 7, player=2,
                              piece_type=Type.King)
        self.add_piece(10, 5, player=3, piece_type=Type.Rook)
        self.add_piece(10, 9, player=4, piece_type=Type.Rook)
        self.game.step(Action(5, 5, 5, 7))

        self.assert_piece_at(rook, 5, 7)
        self.assertNotIn(king, self.players[2].Figures)
        self.assertTrue(self.players[2].IsDefeated)
        self.assertEqual(self.players[1].Score, king.get_value())
        self.assertEqual(self.game.current_player, 3)
        self.assertFalse(self.game.isgameover)

    def test_capture_defeated_players_piece(self):
        rook = self.add_piece(5, 5, piece_type=Type.Rook)
        victim = self.add_piece(5, 7, player=2,
                                piece_type=Type.Bishop)
        self.players[2].IsDefeated = True

        self.game.step(Action(5, 5, 5, 7))

        self.assert_piece_at(rook, 5, 7)
        self.assertNotIn(victim, self.players[2].Figures)
        self.assertEqual(self.players[1].Score, victim.get_value())

    # --------------------------------------------------
    # Action validation
    # --------------------------------------------------

    def test_reject_empty_source(self):
        with self.assertRaises(ValueError):
            self.game.step(Action(5, 5, 5, 6))

        self.assertEqual(self.game.current_player, 1)
        self.assertEqual(self.game.action_history, [])

    def test_reject_other_players_piece(self):
        pawn = self.add_piece(6, 12, player=2)

        with self.assertRaises(ValueError):
            self.game.step(Action(6, 12, 6, 11))

        self.assert_piece_at(pawn, 6, 12)
        self.assertEqual(self.game.current_player, 1)
        self.assertEqual(self.game.action_history, [])

    def test_reject_illegal_move(self):
        rook = self.add_piece(5, 5, piece_type=Type.Rook)

        with self.assertRaises(ValueError):
            self.game.step(Action(5, 5, 6, 6))

        self.assert_piece_at(rook, 5, 5)
        self.assertFalse(rook.HasMoved)
        self.assertEqual(self.game.current_player, 1)
        self.assertEqual(self.game.action_history, [])

    def test_reject_move_onto_friendly_piece(self):
        rook = self.add_piece(5, 5, piece_type=Type.Rook)
        blocker = self.add_piece(5, 7, piece_type=Type.Pawn)

        with self.assertRaises(ValueError):
            self.game.step(Action(5, 5, 5, 7))

        self.assert_piece_at(rook, 5, 5)
        self.assert_piece_at(blocker, 5, 7)
        self.assertEqual(self.players[1].Score, 0)

    def test_reject_move_through_blocker(self):
        rook = self.add_piece(5, 5, piece_type=Type.Rook)
        blocker = self.add_piece(5, 6, player=2)

        with self.assertRaises(ValueError):
            self.game.step(Action(5, 5, 5, 7))

        self.assert_piece_at(rook, 5, 5)
        self.assert_piece_at(blocker, 5, 6)

    # --------------------------------------------------
    # Turn progression
    # --------------------------------------------------

    def test_turn_rotation_and_move_number(self):
        for player, row in enumerate((4, 6, 8, 10), start=1):
            self.add_piece(row, 5, player, Type.Knight)

        expected = (
            (1, 4, 2, 1),
            (2, 6, 3, 1),
            (3, 8, 4, 1),
            (4, 10, 1, 2),
        )

        for player, row, next_player, move_number in expected:
            with self.subTest(player=player):
                self.game.step(Action(row, 5, row + 2, 6))
                self.assertEqual(self.game.current_player, next_player)
                self.assertEqual(self.game.move_number, move_number)

    def test_skip_defeated_players(self):
        self.players[2].IsDefeated = True
        self.players[4].IsDefeated = True

        rook1 = self.add_piece(5, 5, player=1,
                               piece_type=Type.Rook)
        rook3 = self.add_piece(8, 8, player=3,
                               piece_type=Type.Rook)

        self.game.step(Action(5, 5, 5, 6))
        self.assertEqual(self.game.current_player, 3)
        self.assert_piece_at(rook1, 5, 6)

        self.game.step(Action(8, 8, 8, 9))
        self.assertEqual(self.game.current_player, 1)
        self.assertEqual(self.game.move_number, 2)
        self.assert_piece_at(rook3, 8, 9)

    # --------------------------------------------------
    # Action history
    # --------------------------------------------------

    def test_action_history(self):
        pawn1 = self.add_piece(1, 6, player=1)
        pawn2 = self.add_piece(6, 12, player=2)

        action1 = Action(1, 6, 2, 6)
        action2 = Action(6, 12, 6, 11)

        self.game.step(action1)
        self.game.step(action2)

        self.assertEqual(self.game.action_history, [action1, action2])
        self.assert_piece_at(pawn1, 2, 6)
        self.assert_piece_at(pawn2, 6, 11)

    def test_rejected_action_does_not_enter_history(self):
        pawn = self.add_piece(1, 6)
        
        #add pices to other players so game is not over.
        self.add_piece(10, 5, player=2, piece_type=Type.Rook)
        self.add_piece(10, 9, player=3, piece_type=Type.Rook)
        self.add_piece(5, 10, player=4, piece_type=Type.Rook)

        valid = Action(1, 6, 2, 6)
        invalid = Action(2, 6, 4, 6)

        self.game.step(valid)

        with self.assertRaises(ValueError):
            self.game.step(invalid)

        self.assertEqual(self.game.action_history, [valid])
        self.assert_piece_at(pawn, 2, 6)

    # --------------------------------------------------
    # New game
    # --------------------------------------------------

    def test_new_game_initializes_starting_position(self):
        self.game.new_game()

        self.assertEqual(self.game.current_player, 1)
        self.assertEqual(self.game.move_number, 1)
        self.assertFalse(self.game.isgameover)
        self.assertEqual(len(self.game.action_history), 0)

        all_pieces = [
            piece
            for player in self.players.values()
            for piece in player.Figures
        ]

        self.assertEqual(len(all_pieces), 64)

        for player in self.players.values():
            with self.subTest(player=player.Which_Player):
                self.assertEqual(len(player.Figures), 16)
                self.assertEqual(
                    sum(p.Type == Type.King for p in player.Figures),
                    1,
                )
                self.assertFalse(player.IsDefeated)

        for piece in all_pieces:
            self.assertIs(
                self.board.get_figure(piece.X, piece.Y),
                piece,
            )

    def test_new_game_resets_state(self):
        self.game.new_game()

        pawn = self.board.get_figure(1, 6)
        self.assertIsNotNone(pawn)

        self.game.step(Action(1, 6, 2, 6))
        self.players[2].IsDefeated = True
        self.players[1].Score = 12
        self.players[1].Reward = 5
        self.board.en_passants[(4, 6)] = 1
        self.game.isgameover = True

        self.game.new_game()

        self.assertEqual(self.game.current_player, 1)
        self.assertEqual(self.game.move_number, 1)
        self.assertFalse(self.game.isgameover)
        self.assertEqual(self.game.action_history, [])
        self.assertEqual(self.board.en_passants, {})
        self.assertIsNone(self.game.selected_figure)
        self.assertEqual(self.game.current_actions, [])
        self.assertEqual(self.game.action_lookup, {})

        for player in self.players.values():
            with self.subTest(player=player.Which_Player):
                self.assertFalse(player.IsDefeated)
                self.assertEqual(player.Score, 0)
                self.assertEqual(player.Reward, 0)
                self.assertEqual(
                    player.time_ms,
                    player.start_time_ms,
                )
                self.assertEqual(len(player.Figures), 16)

        self.assertIsNotNone(self.board.get_figure(1, 6))
        self.assertIsNone(self.board.get_figure(2, 6))

    # --------------------------------------------------
    # Selection
    # --------------------------------------------------

    def test_select_current_players_piece(self):
        pawn = self.add_piece(1, 6)

        highlights = self.game.select_figure(1, 6)

        self.assertIs(self.game.selected_figure, pawn)
        self.assertEqual(
            set(self.game.current_actions),
            {
                Action(1, 6, 2, 6),
                Action(1, 6, 3, 6, special="double"),
            },
        )
        self.assertEqual(highlights[2][6], 1)
        self.assertEqual(highlights[3][6], 1)

    def test_select_other_players_piece(self):
        self.add_piece(6, 12, player=2)

        highlights = self.game.select_figure(6, 12)

        self.assertIsNone(self.game.selected_figure)
        self.assertEqual(self.game.current_actions, [])
        self.assertTrue(all(value == 0 for row in highlights for value in row))

    def test_select_empty_square(self):
        highlights = self.game.select_figure(5, 5)

        self.assertIsNone(self.game.selected_figure)
        self.assertEqual(self.game.current_actions, [])
        self.assertTrue(all(value == 0 for row in highlights for value in row))

    def test_clear_selection(self):
        self.add_piece(1, 6)
        self.game.select_figure(1, 6)

        self.game.clear_selection()

        self.assertIsNone(self.game.selected_figure)
        self.assertEqual(self.game.current_actions, [])
        self.assertEqual(self.game.action_lookup, {})


if __name__ == "__main__":
    unittest.main()
