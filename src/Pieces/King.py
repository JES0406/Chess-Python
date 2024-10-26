from Pieces.Piece import Piece

class King(Piece):
    def __init__(self, color) -> None:
        super().__init__(color, 'king')
        self.image = self.get_image()

    def move(self, target_position, board):
            """
            Moves the king to the target position if the move is valid.
            :param target_position: Tuple (row, col) representing the target position on the board.
            :param board: A 2D list (8x8) representing the chess board.
            :return: Boolean indicating whether the move was successful.
            """
            current_letter, current_number, target_letter, target_number,  current_col, target_col, row_diff, col_diff = self.get_crdinated(target_position)
            # Check if the target position is one square away in any direction
            if row_diff <= 1 and col_diff <= 1:
                # Ensure the move is within the board boundaries
                if 0 <= target_number - 1 < 8 and 0 <= target_col < 8:
                    target_piece = board[target_number - 1][target_col]
                    
                    # Allow the move if the target square is empty or occupied by an enemy piece
                    if target_piece is None or target_piece.color != self.color:
                        self.pos = target_position
                        return True

            # Invalid move for the king
            return False