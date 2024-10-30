from src.Pieces.Piece import Piece

class King(Piece):
    def __init__(self, color) -> None:
        super().__init__(color, 'king')
        self.image = self.get_image()

    def is_move_valid(self, target_position, board, take):
            current_letter, current_number, target_letter, target_number,  current_col, target_col, row_diff, col_diff = self.get_coordinated(target_position)
            # Check if the target position is one square away in any direction
            if row_diff <= 1 and col_diff <= 1:
                # Ensure the move is within the board boundaries
                if 0 <= target_number - 1 < 8 and 0 <= target_col < 8:
                    return self.taking_logic(board, target_position, take)

            # Invalid move for the king
            return False, 'invalid'