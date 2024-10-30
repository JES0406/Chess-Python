from src.Pieces.Piece import Piece

class Queen(Piece):
    def __init__(self, color) -> None:
        super().__init__(color, 'queen')
        self.image = self.get_image()

    def is_move_valid(self, target_position, board, take):
        current_letter, current_number, target_letter, target_number, current_col, target_col, row_diff, col_diff = self.get_coordinated(target_position)

        # Check if the move is in a straight line (like a rook) or a diagonal (like a bishop)
        if row_diff == 0 or col_diff == 0 or row_diff == col_diff:
            # Determine movement direction
            row_step = 0 if row_diff == 0 else (1 if target_number > current_number else -1)
            col_step = 0 if col_diff == 0 else (1 if target_col > current_col else -1)

            # Check path for any blocking pieces
            steps = max(row_diff, col_diff)
            for step in range(1, steps):
                intermediate_position = (chr(ord(current_letter) + step * col_step), current_number + step * row_step)
                if board[intermediate_position] is not None:
                    return False, 'Path blocked'  # Path is blocked

            # Check if target square is empty or contains an enemy piece
            return self.taking_logic(board, target_position, take)

        # Invalid move for the queen
        return False, 'Invalid move'




