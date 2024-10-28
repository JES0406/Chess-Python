from src.Pieces.Piece import Piece

class Pawn(Piece):
    def __init__(self, color) -> None:
        super().__init__(color, 'pawn')
        self.image = self.get_image()
    
    def is_move_valid(self, target_position, board, take):
        current_letter, current_number, target_letter, target_number,  current_col, target_col, row_diff, col_diff = self.get_coordinated(target_position)

        direction = 1 if self.color == "w" else -1

        if target_letter == current_letter and target_number == current_number + direction:
            if board[target_number][target_col] is None:  # Ensure the square is empty
                return True, 'all good'

        # First move, allow two squares forward
        if (self.color == "w" and current_number == 2) or (self.color == "b" and current_number == 7):
            # print(current_number + direction)
            # print(board[current_number + direction][target_col], board[target_number][target_col])
            if target_letter == current_letter and target_number == current_number + 2 * direction:
                
                if (board[current_number + direction][target_col] is None and 
                    board[target_number][target_col] is None):  # Both squares should be empty
                    return True, 'all good'

        # Capture diagonally
        if abs(ord(target_letter) - ord(current_letter)) == 1 and target_number == current_number + direction:
            if board[target_number][target_col] is not None and board[target_number][target_col].color != self.color:
                if not take:
                    return False, 'Move not marked as take, perhaps you forgot about a the x?'
                return True, 'all good'

        # Invalid move
        return False, 'not valid'