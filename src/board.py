from typing import Any
from src.constants import numbers, letters, tile_size, board_size, theme, font
import pygame
from src.Pieces.Pieces import *

class Board:
    def __init__(self) -> None:
        self._board = [[None for i in range(len(numbers))] for j in range(len(letters))]

    @property
    def board(self):
        return self._board
    
    def initialize_board(self):
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for col in range(board_size):
            self.board[1][col] = Pawn('w')    # Place pawns on the second rank
            self.board[1][col].pos = (letters[col], 2)
            self.board[0][col] = piece_order[col]('w')  # Place main pieces on the first rank
            self.board[0][col].pos = (letters[col], 1)

        # Place black pieces (top of the board)
        for col in range(board_size):
            self.board[6][col] = Pawn('b')    # Place pawns on the seventh rank
            self.board[6][col].pos = (letters[col], 7)
            self.board[7][col] = piece_order[col]('b')  # Place main pieces on the eighth rank
            self.board[7][col].pos = (letters[col], 8)

    def find_pieces(self, color, piece_type, target_square, disambiguation=None, take = None):
        """
        Finds all pieces of a given type and color that could legally move to a target square.
        :param color: The color of the piece ('white' or 'black').
        :param piece_type: The type of the piece ('pawn', 'knight', 'bishop', 'rook', 'queen', or 'king').
        :param target_square: The square the piece is moving to (e.g., 'd4').
        :param disambiguation: Optional disambiguation string to specify file or rank of the piece.
        :return: A list of piece objects that could move to the target square.
        """
        possible_pieces = []

        # Loop through all squares on the board to find pieces matching the color and type
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                
                # Skip empty squares or pieces of the wrong color/type
                if piece is None or piece.color != color or piece.type != piece_type:
                    continue
                # Check if the piece can legally move to the target square
                valid = piece.is_move_valid(target_square, self.board, take)
                if valid[0]:
                    # If disambiguation is provided, check if it matches
                    if disambiguation:
                        # If disambiguation is a file (e.g., 'Nbd2'), it should match the piece's current file
                        if disambiguation in letters and piece.pos[0] != disambiguation:
                            continue
                        # If disambiguation is a rank (e.g., 'N2d2'), it should match the piece's current rank
                        if disambiguation in numbers and str(piece.pos[1]) != disambiguation:
                            continue
                    
                    # Add the piece to the list of possible pieces
                    possible_pieces.append(piece)
                # else:
                #     print(valid[1]) if piece.color != "w" else None

        return possible_pieces
    
    def is_castling_valid(self, color, kingside):
        row = 0 if color == "w" else 7
        king_col = 4
        rook_col = 7 if kingside else 0
        step = 1 if kingside else -1

        # Retrieve the king and rook
        king = self.board[row][king_col]
        rook = self.board[row][rook_col]

        # Check if the king and rook are in the correct positions and are of the correct color
        if not isinstance(king, King) or king.color != color or king.has_moved:
            return False
        if not isinstance(rook, Rook) or rook.color != color or rook.has_moved:
            return False

        # Check the path between the king and rook for any blocking pieces
        for col in range(king_col + step, rook_col, step):
            if self.board[row][col] is not None:
                return False

        # Check that no square the king moves through (including starting and ending) is under attack
        for col in range(king_col, king_col + 2 * step, step):
            if self.is_square_under_attack((row, col), color):
                return False

        # If all conditions are satisfied, castling is valid
        return True
    
    def is_square_under_attack(self, square, color):
        """
        Checks if a square is under attack by the opponent.
        :param square: Tuple (row, col) of the square to check.
        :param color: The color of the player making the check (used to identify opponent).
        :return: True if the square is under attack, False otherwise.
        """
        opponent_color = "b" if color == "w" else "w"

        # Check if any opponent piece can move to the square
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and piece.color == opponent_color:
                    if self.is_move_valid(piece, square):
                        return True
        return False
    
    def draw(self, screen):
    # Assuming tile_size is imported from another module, ensure it is referenced here
        for row in range(board_size):
            for col in range(board_size):
                # Determine the color of the tile based on position (alternating pattern)
                color = "dark" if (row + col) % 2 == 0 else "light"
                path_of_bg = rf"Visuals\square_{theme}_{color}_png_shadow_128px.png"
                
                # Load the background tile image afresh for each tile to avoid carryover
                tile_image = pygame.image.load(path_of_bg)

                # Check if there’s a piece on this square
                piece = self.board[row][col]
                if piece is not None:
                    # print(f"Drawing {piece.type} at ({row}, {col}) - Expected position: {piece.pos}")
                    piece_path = piece.image  # This should point to the correct image path for the piece
                    piece_image = pygame.image.load(piece_path)
                    piece_image = pygame.transform.scale(piece_image, (tile_size, tile_size))
                    tile_image.blit(piece_image, (0, 0))  # Overlay the piece image onto the tile

                # Calculate the position on the screen
                x_pos = col * tile_size + 25
                y_pos = (7 - row) * tile_size + 25  # Adjust for bottom-to-top display
                screen.blit(tile_image, (x_pos, y_pos))

    def __getitem__(self, item):
        return self.board[item[1]][ord(item[0]) - ord('a')]
    
    def __setitem__(self, key, value):
        # print("changes", key, value)
        self.board[key[1]-1][ord(key[0]) - ord('a')-1] = value
