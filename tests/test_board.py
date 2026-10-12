import unittest

from Persistence.Board import Board
from Persistence.Figure import Figure
from Persistence.Type import Type


class TestBoard(unittest.TestCase):
    
    def setUp(self):
        self.board = Board()
        
    def add_figure(self, row, col, player=1, figure_type=Type.Pawn):
        figure = Figure(row, col, figure_type, player)
        self.board.place_figure(figure, row, col)
        return figure
    
    def test_board_shape(self):
        shape = self.board.empty_board()
        self.assertEqual(len(shape), 14)
        self.assertTrue(all(len(row) == 14 for row in shape))
        self.assertEqual(len(self.board.figure_board), 14)
        self.assertTrue(all(len(row) == 14 for row in self.board.figure_board))
    
    def test_board_boundaries(self):
        valid = [(0, 3), (3, 0), (10, 13), (13, 10), (6, 6)]
        invalid = [
            (0, 0), (2, 2), (11, 11), (13, 13),
            (-1, 5), (5, -1), (14, 5), (5, 14),
        ]
        for pos in valid:
            with self.subTest(pos=pos):
                self.assertTrue(self.board.in_bounds(*pos))
        for pos in invalid:
            with self.subTest(pos=pos):
                self.assertFalse(self.board.in_bounds(*pos))

    def test_place_and_get_figure(self):
        figure = self.add_figure(5, 5)
        self.assertIs(self.board.get_figure(5, 5), figure)
        self.assertIsNone(self.board.get_figure(5, 6))

    def test_place_figure_on_occupied_square(self):
        self.add_figure(5, 5)
        other = Figure(5, 5, Type.Rook, 2)

        with self.assertRaises(ValueError):
            self.board.place_figure(other, 5, 5)

    def test_place_figure_out_of_bounds(self):
        figure = Figure(0, 0, Type.Pawn, 1)

        for pos in [(0, 0), (-1, 5), (14, 5)]:
            with self.subTest(pos=pos):
                with self.assertRaises(ValueError):
                    self.board.place_figure(figure, *pos)

    def test_remove_figure(self):
        figure = self.add_figure(5, 5)

        removed = self.board.remove_figure(5, 5)

        self.assertIs(removed, figure)
        self.assertIsNone(self.board.get_figure(5, 5))

    def test_remove_missing_figure(self):
        with self.assertRaises(ValueError):
            self.board.remove_figure(5, 5)

    def test_remove_figure_out_of_bounds(self):
        with self.assertRaises(ValueError):
            self.board.remove_figure(0, 0)

    def test_replace_figure(self):
        original = self.add_figure(5, 5)
        replacement = Figure(5, 5, Type.Queen, 2)

        self.board.replace_figure(replacement, 5, 5)

        self.assertIs(self.board.get_figure(5, 5), replacement)
        self.assertIsNot(self.board.get_figure(5, 5), original)

    def test_occupancy(self):
        self.add_figure(5, 5, player=1)

        self.assertTrue(self.board.is_friendly(1, 5, 5))
        self.assertFalse(self.board.is_hit(1, 5, 5))

        self.assertTrue(self.board.is_hit(2, 5, 5))
        self.assertFalse(self.board.is_friendly(2, 5, 5))

        self.assertFalse(self.board.is_free(5, 5))
        self.assertTrue(self.board.is_free(5, 6))

    def test_invalid_squares_are_not_occupiable(self):
        for pos in [(0, 0), (-1, 5), (14, 5)]:
            with self.subTest(pos=pos):
                self.assertFalse(self.board.is_free(*pos))
                self.assertFalse(self.board.is_hit(1, *pos))
                self.assertFalse(self.board.is_friendly(1, *pos))

    def test_tuple_coordinates(self):
        figure = self.add_figure(5, 5)

        self.assertTrue(self.board.in_bounds((5, 5)))
        self.assertIs(self.board.get_figure((5, 5)), figure)
        self.assertTrue(self.board.is_friendly(1, (5, 5)))
        self.assertFalse(self.board.is_free((5, 5)))

        self.assertIs(self.board.remove_figure((5, 5)), figure)

    def test_clear_en_passants_for_player(self):
        self.board.en_passants = {
            (2, 5): 1,
            (6, 8): 2,
            (9, 5): 1,
            (7, 7): 3,
        }

        self.board.clear_en_passants(1)

        self.assertEqual(
            self.board.en_passants,
            {(6, 8): 2, (7, 7): 3},
        )











if __name__ == "__main__":
    unittest.main()