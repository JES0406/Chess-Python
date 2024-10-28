from src.Pieces.Piece import Piece

class Rook(Piece):
    def __init__(self, color) -> None:
        super().__init__(color, 'rook')
        self.image = self.get_image()

    def is_move_valid(self, target_position, board, take):
        current_letter, current_number, target_letter, target_number,  current_col, target_col, row_diff, col_diff = self.get_coordinated(target_position)

        if row_diff == 0 or col_diff == 0:
            # Determine movement direction
            row_step = 0 if row_diff == 0 else (1 if target_number > current_number else -1)
            col_step = 0 if col_diff == 0 else (1 if target_col > current_col else -1)

            # Check path for any blocking pieces
            steps = max(row_diff, col_diff)
            for step in range(1, steps):
                if board[current_number + step * row_step - 1][current_col + step * col_step] is not None:
                    return False, 'path is blocked'  # Path is blocked

            # Check if target square is empty or contains an enemy piece
            target_piece = board[target_number - 1][target_col]
            if target_piece is None or target_piece.color != self.color:
                if not take:
                    return False, 'Move not marked as take, perhaps you forgot about a the x?'
                return True, 'all good'

        # Invalid move for the rook
        return False, 'invalid'