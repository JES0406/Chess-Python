from src.Pieces.Piece import Piece

class Pawn(Piece):
    def __init__(self, color) -> None:
        super().__init__(color, 'pawn')
        self.image = self.get_image()
    
    def is_move_valid(self, target_position, board, take):
        current_letter, current_number, target_letter, target_number,  current_col, target_col, row_diff, col_diff = self.get_coordinated(target_position)

        direction = 1 if self.color == "w" else -1

        one_step_pos = (current_letter, current_number + direction)

        # One square forward
        if target_letter == current_letter and target_number == current_number + direction:
            if board[target_position] is None:  # Ensure the target square is empty
                return True, 'One fowards'

        # First move: allow two squares forward
        if (self.color == "w" and current_number == 2) or (self.color == "b" and current_number == 7):
            if target_letter == current_letter and target_number == current_number + 2 * direction:
                if board[one_step_pos] is None and board[target_position] is None:  # Both squares should be empty
                    return True, 'Two fowards'

        # Capture diagonally
        if abs(ord(target_letter) - ord(current_letter)) == 1 and target_number == current_number + direction and take:
            if board.last_pawn_move == (target_letter, target_number - direction): # En passant
                return True, "En passant"
            return self.taking_logic(board, target_position, take)

        # Invalid move
        return False, 'not valid'