from src.Pieces.Piece import Piece

class Knight(Piece):
    def __init__(self, color) -> None:
        super().__init__(color, 'knight')
        self.image = self.get_image()

    def is_move_valid(self, target_position, board):
        current_letter, current_number, target_letter, target_number,  current_col, target_col, row_diff, col_diff = self.get_coordinated(target_position)

        # Knight moves in an "L" shape: two squares in one direction and one in the other
        if (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2):
            target_piece = board[target_number - 1][target_col]
            # Knight can capture an opponent's piece or move to an empty square
            if target_piece is None or target_piece.color != self.color:
                return True, 'all good'

        # Invalid move for the knight
        return False, 'invalid'
