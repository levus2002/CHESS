import unittest
from Persistence.Board import Board, Action
from Persistence.Type import Type
from Persistence.Figure import Figure

class MockFigure(Figure):
    def __init__(self, x, y, player, type):
        self.X = x
        self.Y = y
        self.Player = player
        self.Type = type
        self.HasMoved = False

    def move(self, x, y):
        self.X = x
        self.Y = y
        self.HasMoved = True


class MockPlayer:
    def __init__(self, player_id):
        self.player_id = player_id
        self.figures = []
        self.IsDefeated = False
        self.Reward = 0

    def add_figure(self, fig):
        self.figures.append(fig)

    def remove_figure(self, fig):
        self.figures.remove(fig)

    def get_figure(self, x, y):
        for f in self.figures:
            if f.X == x and f.Y == y:
                return f
        return None

    def get_figure_pos_list(self):
        return [(f.X, f.Y) for f in self.figures]

class TestBoard(unittest.TestCase):

    def setUp(self):
        self.p1 = MockPlayer(1)
        self.p2 = MockPlayer(2)
        self.p3 = MockPlayer(3)
        self.p4 = MockPlayer(4)

        self.board = Board(self.p1, self.p2, self.p3, self.p4)

        self.board.board_state = self.board.empty_board()
        
    def addfig(self,x,y,p,t):    
        fig = MockFigure(x, y, p, t)
        match p:
            case 1:
                self.p1.add_figure(fig)
            case 2:
                self.p2.add_figure(fig)
            case 3:
                self.p3.add_figure(fig)
            case 4:
                self.p4.add_figure(fig)
        self.board.board_state[x][y] = p
        return fig

    def test_board_shape(self):
        board = self.board.empty_board()
        self.assertEqual(len(board), 14)
        self.assertEqual(len(board[0]), 14)
        
        
#-----------------------------------------------------
#                  FIGURE TESTS
    def test_add_and_get_figure(self):
        fig = MockFigure(5, 5, 1, Type.Pawn)
        self.p1.add_figure(fig)
        self.board.board_state[5][5] = 1

        result = self.board.get_figure(5, 5)

        self.assertIsNotNone(result)
        self.assertEqual(result.X, 5) # type: ignore
        self.assertEqual(result.Y, 5) # type: ignore


    def test_select_figure_none(self):
        x,y=3,3
        self.board.select_figure(x, y)
        fig=self.board.get_figure(x,y)
        self.assertIsNone(fig)
        self.assertIsNone(self.board.selected_figure)
        self.assertEqual(self.board.current_actions, [])
        self.assertEqual(self.board.board_state[x][y],0)
        
    def test_pawn_moves(self):
        fig=self.addfig(1, 8, 1, Type.Pawn)
        self.assertFalse(fig.HasMoved)
        moves = self.board.get_moves(fig)
        self.assertEqual(len(moves), 2)
        targets = {(a.to_row, a.to_col) for a in moves}
        self.assertIn((2, 8), targets)
        self.assertIn((3, 8), targets)
        
        fig.move(3,8)
        moves = self.board.get_moves(fig)
        self.assertEqual(len(moves), 1)
        targets = {(a.to_row, a.to_col) for a in moves}
        self.assertIn((4, 8), targets)
        
    def test_knight_moves(self):
        fig=self.addfig(3, 3, 1, Type.Knight)
        self.addfig(1, 4, 1, Type.Pawn)
        self.addfig(4, 5, 2, Type.Pawn)
        moves = self.board.get_moves(fig)
        self.assertEqual(len(moves), 5)
        targets = {(a.to_row, a.to_col) for a in moves}
        self.assertIn((5,4), targets)
        self.assertIn((5,2), targets)
        self.assertIn((2,5), targets)
        self.assertIn((4,5), targets)
        self.assertIn((4,1), targets)
        self.assertNotIn((1,2), targets)
        self.assertNotIn((2,1), targets)
        self.assertNotIn((1,4), targets)
    
    def test_bishop_moves(self):
        fig=self.addfig(5, 5, 1, Type.Bishop)
        self.addfig(8, 2, 1, Type.Pawn)
        self.addfig(1, 9, 2, Type.Pawn)
        moves = self.board.get_moves(fig)
        self.assertEqual(len(moves),13)
        targets = {(a.to_row, a.to_col) for a in moves}
        self.assertIn((7, 3), targets)
        self.assertNotIn((8, 2), targets)
        self.assertIn((3, 3), targets)
        self.assertNotIn((2, 2), targets)
        self.assertIn((2, 8), targets)
        self.assertIn((1, 9), targets)
        self.assertNotIn((0, 10), targets)
        self.assertIn((10, 10), targets)
        self.assertNotIn((11, 11), targets)
        
        
        
    def test_rook_moves(self):
        fig=self.addfig(7, 2, 1, Type.Rook)
        self.addfig(7, 10, 1, Type.Pawn)
        self.addfig(9, 2, 2, Type.Pawn)
        moves = self.board.get_moves(fig)
        self.assertEqual(len(moves), 15)
        targets = {(a.to_row, a.to_col) for a in moves}
        
        self.assertIn((7, 9), targets)
        self.assertNotIn((7, 10), targets)
        self.assertNotIn((7, 13), targets)
        self.assertIn((3, 2), targets)
        self.assertNotIn((2, 2), targets)
        self.assertIn((7, 0), targets)
        self.assertNotIn((7, -1), targets)
        self.assertIn((9, 2), targets)   
        self.assertNotIn((10, 2), targets)   
 
    def test_queen_moves(self):
        fig=self.addfig(4, 2, 1, Type.Queen)
        self.addfig(6, 4, 1, Type.Pawn)
        self.addfig(7, 2, 2, Type.Pawn)
        self.addfig(4, 8, 3, Type.Bishop)
        
        moves = self.board.get_moves(fig)
        self.assertEqual(len(moves), 20)
        targets = {(a.to_row, a.to_col) for a in moves}
        self.assertIn((3, 1), targets)
        self.assertIn((3, 2), targets)
        self.assertIn((4, 1), targets)
        self.assertIn((4, 0), targets)
        self.assertIn((0, 6), targets)
        self.assertIn((5, 3), targets)
        self.assertNotIn((6, 4), targets)
        self.assertIn((7, 2), targets)
        self.assertNotIn((8, 2), targets)
        self.assertIn((4, 8), targets)
        self.assertNotIn((4, 9), targets)
        
    def test_king_moves(self):
        fig=self.addfig(3, 3, 1, Type.King)
        self.addfig(4, 4, 1, Type.Pawn)
        self.addfig(4, 2, 2, Type.Pawn)
        self.addfig(2, 4, 3, Type.Bishop)
        
        moves = self.board.get_moves(fig)
        self.assertEqual(len(moves), 6)
        targets = {(a.to_row, a.to_col) for a in moves}
        self.assertIn((3, 2), targets)
        self.assertIn((2, 3), targets)
        self.assertIn((2, 4), targets)
        self.assertIn((3, 4), targets)
        self.assertIn((4, 2), targets)
        self.assertIn((4, 3), targets)
        self.assertNotIn((4, 4), targets)
#------------------------------------------------------
#               SPECIAL MOVE TESTS

    def test_en_passant(self):
        self.addfig(7, 0, 1, Type.King)
        self.addfig(8, 0, 2, Type.King)
        self.p3.IsDefeated=True
        self.p4.IsDefeated=True
        pawn1=self.addfig(1, 10, 1, Type.Pawn)
        pawn2=self.addfig(3, 12, 2, Type.Pawn)
        action1=Action(1,10,2,10,None,None)
        action2=Action(3,12,3,10,"double",None)
        action3=Action(2,10,3,11,"en_passant",None)
        self.assertEqual(self.board.current_player_index, 1)
        self.board.make_move(action1)
        self.assertEqual(pawn1.X, 2)
        self.assertEqual(pawn1.Y, 10)
        self.assertEqual(self.board.board_state[2][10],1)
        self.assertEqual(self.board.board_state[1][10],0)
        
        self.assertEqual(self.board.current_player_index, 2)
        self.assertFalse(pawn2.HasMoved)
        self.board.make_move(action2)
        
        self.assertEqual(self.board.current_player_index, 1)
        self.assertEqual(len(self.board.en_passants),1)
        
        self.assertEqual(pawn2.X, 3)
        self.assertEqual(pawn2.Y, 10)
        self.assertEqual(self.board.board_state[3][12],0)
        self.assertEqual(self.board.board_state[3][10],2)
        
        self.board.make_move(action3)
        self.assertEqual(pawn1.X, 3)
        self.assertEqual(pawn1.Y, 11)
        self.assertEqual(self.board.board_state[3][11],1)
        self.assertEqual(self.board.board_state[3][12],0)
        self.assertEqual(self.board.board_state[2][10],0)
        self.assertEqual(len(self.p2.figures),1)
        
        
    def test_king_castle(self):
        rook1=self.addfig(0, 3, 1, Type.Rook)
        king1=self.addfig(0, 6, 1, Type.King)
        self.p2.IsDefeated=True
        self.p3.IsDefeated=True
        king4=self.addfig(6, 0, 4, Type.King)


        self.assertFalse(king1.HasMoved)
        self.assertFalse(king4.HasMoved)
        self.assertFalse(rook1.HasMoved)
      
        self.assertEqual(self.board.board_state[0][5],0)
        self.assertEqual(self.board.board_state[0][4],0)
        self.assertEqual(self.board.board_state[0][6],1)
        self.assertEqual(self.board.board_state[0][3],1)
        
        action1=Action(0,6,0,4,"KingCastle",None)
        self.assertEqual(self.board.current_player_index, 1)
        self.board.make_move(action1)
        self.assertTrue(king1.HasMoved)
        self.assertTrue(rook1.HasMoved)
        self.assertEqual(self.board.board_state[0][4],1)
        self.assertEqual(self.board.board_state[0][5],1)
        self.assertEqual(self.board.board_state[0][6],0)
        self.assertEqual(self.board.board_state[0][3],0)
        self.assertEqual(king1.X, 0)
        self.assertEqual(king1.Y, 4)
        self.assertEqual(rook1.X, 0)
        self.assertEqual(rook1.Y, 5)
        
        self.assertEqual(self.board.current_player_index, 4)

        #no king rook
        moves = self.board.get_moves(king4)
        self.assertEqual(len(moves), 5)
        targets = {(a.to_row, a.to_col) for a in moves}
        self.assertNotIn((4, 0), targets)
        
        rook4=self.addfig(3, 0, 4, Type.Rook)
        rook4.HasMoved=True
        self.assertTrue(rook4.HasMoved)
               
        # rook exists but it already moved
        moves = self.board.get_moves(king4)
        self.assertEqual(len(moves), 5)
        targets = {(a.to_row, a.to_col) for a in moves}
        self.assertNotIn((4, 0), targets)
        
        rook4.HasMoved=False
        king4.HasMoved=True
        # Rook hasnt moved but king did
        moves = self.board.get_moves(king4)
        self.assertEqual(len(moves), 5)
        targets = {(a.to_row, a.to_col) for a in moves}
        self.assertNotIn((4, 0), targets)
        
        king4.HasMoved=False
        self.addfig(4,0,3,Type.Rook)
        self.assertEqual(self.board.board_state[3][0],4)
        self.assertEqual(self.board.board_state[4][0],3)
        self.assertEqual(self.board.board_state[5][0],0)
        self.assertEqual(self.board.board_state[6][0],4)
        self.assertFalse(rook4.HasMoved)
        self.assertFalse(king4.HasMoved)
        #king and rook hasnt moved, but a piece occupies way
        moves = self.board.get_moves(king4)
        self.assertEqual(len(moves), 5)
        targets = {(a.to_row, a.to_col) for a in moves}
        self.assertNotIn((4, 0), targets)
        
    def test_queen_castle(self):
        rook1=self.addfig(0, 10, 1, Type.Rook)
        king1=self.addfig(0, 6, 1, Type.King)
        self.p2.IsDefeated=True
        self.p3.IsDefeated=True

        self.assertFalse(king1.HasMoved)

        self.assertFalse(rook1.HasMoved)
        
        self.assertEqual(self.board.board_state[0][6],1)
        self.assertEqual(self.board.board_state[0][7],0)
        self.assertEqual(self.board.board_state[0][8],0)
        self.assertEqual(self.board.board_state[0][9],0)
        self.assertEqual(self.board.board_state[0][10],1)
            
        action1=Action(0,6,0,8,"QueenCastle",None)
        self.assertEqual(self.board.current_player_index, 1)
        self.board.make_move(action1)
        self.assertTrue(king1.HasMoved)
        self.assertTrue(rook1.HasMoved)
        self.assertEqual(self.board.board_state[0][6],0)
        self.assertEqual(self.board.board_state[0][7],1)
        self.assertEqual(self.board.board_state[0][8],1)
        self.assertEqual(self.board.board_state[0][9],0)
        self.assertEqual(self.board.board_state[0][10],0)
        self.assertEqual(king1.X, 0)
        self.assertEqual(king1.Y, 8)
        self.assertEqual(rook1.X, 0)
        self.assertEqual(rook1.Y, 7)
        
    
    def test_promotion(self):
        king1=self.addfig( 10,0, 1, Type.King)
        king2=self.addfig( 6,0, 2, Type.King)
        self.p3.IsDefeated=True
        self.p4.IsDefeated=True
        self.addfig(0,8,1,Type.Knight)
        pawn1=self.addfig(6, 7, 1, Type.Pawn)
        pawn2=self.addfig(1, 9, 2, Type.Pawn)
        action1=Action(6,7,7,7,None,"Q")
        action2=Action(1,9,0,8,None,"R")
        self.assertEqual(self.board.current_player_index, 1)
        self.board.make_move(action1)
        self.assertEqual(pawn1.X,7)
        self.assertEqual(pawn1.Y,7)
        self.assertEqual(pawn1.Type,Type.Queen)
        self.assertEqual(self.board.current_player_index, 2)
        self.board.make_move(action2)
        self.assertEqual(self.board.current_player_index, 1)
        self.assertEqual(pawn2.X,0)
        self.assertEqual(pawn2.Y,8)
        self.assertEqual(pawn2.Type,Type.Rook)
    
    
#----------------------------------------------------
    def test_next_player(self):
        self.board.current_player_index = 1
        self.board.next_player()
        self.assertEqual(self.board.current_player_index, 2)
        self.p3.IsDefeated=True
        self.p4.IsDefeated=True
        self.board.next_player()
        self.assertEqual(self.board.current_player_index, 1)
        self.p2.IsDefeated=True
        self.board.next_player()
        self.assertEqual(self.board.current_player_index, 1)
        self.assertTrue(self.board.is_game_over)
        self.assertEqual(self.board.winner_id,1)
        

    def test_try_move_invalid(self):
        success = self.board.try_move(5, 5)
        self.assertFalse(success)
        
    def test_reward(self):
        king1=self.addfig( 10,0, 1, Type.King)
        king2=self.addfig( 6,0, 2, Type.King)
        self.p3.IsDefeated=True
        self.p4.IsDefeated=True
        self.addfig(7,0,2,Type.Rook)
        self.addfig(2,10,1,Type.Queen)
        self.addfig(10,10,1,Type.Bishop)
        self.addfig(9,12,1,Type.Rook)
        action1=Action(2,10,7,10,None,None)
        action2=Action(7,0,7,10,None,None)
        action3=Action(9,12,10,12,None,None)
        action4=Action(7,10,10,10,None,None)
        action5=Action(10,12,10,10,None,None)
        self.assertEqual(self.board.current_player_index, 1)
        self.board.make_move(action1)
        self.assertEqual(self.p1.Reward, -0.18)
        self.assertEqual(self.board.current_player_index, 2)
        self.board.make_move(action2)
        self.assertEqual(self.p2.Reward, 0.18)
        self.assertEqual(self.board.current_player_index, 1)
        self.board.make_move(action3)
        self.assertEqual(self.p1.Reward, 0)
        self.assertEqual(self.board.current_player_index, 2)
        self.board.make_move(action4)
        self.assertLess(self.p2.Reward, 0)
        self.assertEqual(self.board.current_player_index, 1)
        self.board.make_move(action5)
        self.assertGreater(self.p1.Reward, 0)
        self.assertEqual(self.board.current_player_index, 2)
        

    def test_reward_reset(self):
        self.p1.Reward = 10
        self.board.reset_reward(1)
        self.assertEqual(self.p1.Reward, 0)
        
    def test_get_all_moves(self):
        queen1= self.addfig(3,10,1,Type.Queen)
        rook1=self.addfig(6,6,1,Type.Rook)
        movesq = self.board.get_moves(queen1)
        movesr = self.board.get_moves(rook1)
        self.assertEqual(len(movesq), 39)
        self.assertEqual(len(movesr), 26)
        moves=self.board.get_all_moves(1)
        self.assertEqual(len(moves), 65)

    def test_hit_and_protect_map(self):
        queen1= self.addfig(3,10,1,Type.Queen)
        pawn1=self.addfig(3,8,1,Type.Pawn)
        rook1=self.addfig(5,5,1,Type.Rook)
        self.addfig(4,9,2,Type.Rook)
        hm=self.board.make_hitmap(2)
        pm=self.board.make_protectmap(1)
        self.assertEqual(hm[4][9],1)
        self.assertEqual(hm[4][10],9)
        self.assertEqual(hm[5][10],5)
        self.assertEqual(hm[3][7],0)
        
        
        self.assertEqual(pm[3][9],1)
        self.assertEqual(pm[4][10],1)
        self.assertEqual(pm[3][7],0)

if __name__ == "__main__":
    unittest.main()