from Pieces.Piece import Piece

class Bishop(Piece):
    def __init__(self, color) -> None:
        super().__init__(color, 'bishop')
        self.image = self.get_image()

    def move(self, target_position, board):
        current_letter, current_number, target_letter, target_number,  current_col, target_col, row_diff, col_diff = self.get_crdinated(target_position)

        # Bishop moves diagonally, so row and column difference must be equal
        if row_diff == col_diff:
            # Check path for any blocking pieces
            row_step = 1 if target_number > current_number else -1
            col_step = 1 if target_col > current_col else -1

            for step in range(1, row_diff):
                if board[current_number + step * row_step - 1][current_col + step * col_step] is not None:
                    return False  # Path is blocked

            # Check if target square is empty or contains an enemy piece
            target_piece = board[target_number - 1][target_col]
            if target_piece is None or target_piece.color != self.color:
                self.pos = target_position
                return True

        # Invalid move for the bishop
        return False
