from src.constants import letters, numbers, path_of_piece, piece_size

class Piece:
    def __init__(self, color, _type) -> None:
        self._image = None # Path to the image
        self._pos = (None, None) # (letter, number)
        self._color = color
        self._type = _type
        self._has_moved = False

    @property
    def image(self):
        return self._image
    
    @image.setter
    def image(self, value):
        self._image = value
    
    @property
    def pos(self):
        return self._pos
    
    @pos.setter
    def pos(self, position:tuple):
        if position[0] not in letters:
            raise ValueError("Letter not valid")
        if position[1] not in numbers:
            raise ValueError("Number not valid")
        
        self._pos = position

    @property
    def color(self):
        return self._color
    
    @property
    def type(self):
        return self._type

    @property
    def has_moved(self):
        return self._has_moved
    
    @has_moved.setter
    def has_moved(self, value):
        self._has_moved = value

    def move(self, target_position, board, take):
        """
        Moves the pawn to the target position if the move is valid.
        :param target_position: Tuple (letter, number) representing the target position on the board.
        :param board: A 2D array or dictionary representing the chess board where pieces are stored.
        :return: Boolean indicating whether the move was successful.
        """
        valid = self.is_move_valid(target_position, board, take)
        if valid[0]:
            self.pos = target_position
            self.has_moved = True
        return valid

    def is_move_valid(self, board, target_position, take)->None:
        raise NotImplementedError("This is an abstract class, the method must me overriden")
    
    def get_image(self):
        return path_of_piece.format(color = self.color, piece = self.type, size = piece_size)
    

    def get_coordinated(self, target_position):
        current_letter, current_number = self.pos
        target_letter, target_number = target_position

        # Convert letters (files) to column indices
        current_col = ord(current_letter) - ord('a')
        target_col = ord(target_letter) - ord('a')

        # Calculate the differences in rows and columns
        row_diff = abs(int(target_number) - int(current_number))
        col_diff = abs(target_col - current_col)

        return current_letter, current_number, target_letter, target_number, current_col, target_col, row_diff, col_diff
    
    def __str__(self) -> str:
        return f"{self.type}: position: {self.pos}"

