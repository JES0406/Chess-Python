from src.Pieces.Piece import Piece

class Pawn(Piece):
    def __init__(self, color) -> None:
        super().__init__(color, 'pawn')
        self.image = self.get_image()
    
    def is_move_valid(self, board, target_position):
        current_letter, current_number, target_letter, target_number,  current_col, target_col, row_diff, col_diff = self.get_coordinated(target_position)

        direction = 1 if self.color == "white" else -1

        if target_letter == current_letter and target_number == current_number + direction:
            if board[target_letter][target_number] is None:  # Ensure the square is empty
                return True

        # First move, allow two squares forward
        if (self.color == "white" and current_number == 2) or (self.color == "black" and current_number == 7):
            if target_letter == current_letter and target_number == current_number + 2 * direction:
                if (board[target_letter][current_number + direction] is None and
                        board[target_letter][target_number] is None):  # Both squares should be empty
                    return True

        # Capture diagonally
        if abs(ord(target_letter) - ord(current_letter)) == 1 and target_number == current_number + direction:
            if board[target_letter][target_number] is not None and board[target_letter][target_number].color != self.color:
                return True

        # Invalid move
        return False