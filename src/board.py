from src.constants import numbers, letters, tile_size, board_size, theme
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
            self.board[0][col] = piece_order[col]('w')  # Place main pieces on the first rank

        # Place black pieces (top of the board)
        for col in range(board_size):
            self.board[6][col] = Pawn('b')    # Place pawns on the seventh rank
            self.board[7][col] = piece_order[col]('b')  # Place main pieces on the eighth rank

    def find_pieces(self, color, piece_type, target_square, disambiguation=None):
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
                if self.is_move_valid(piece, (target_square[0], int(target_square[1]))):
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

        return possible_pieces

    def draw(self, screen):
        """
        Draws the chess board with alternating light and dark tiles.
        :param screen: The pygame display surface to draw on.
        """
        for row in range(board_size):
            for col in range(board_size):
                # Determine color of the tile based on position (alternating pattern)
                color = "dark" if (row + col) % 2 == 0 else "light"
                
                # Format the path of the background image based on color and theme
                path_of_bg = rf"Visuals\square_{theme}_{color}_png_shadow_128px.png"
                
                # Load the image and scale it to the tile size
                tile_image = pygame.image.load(path_of_bg)
                # tile_image = pygame.transform.scale(tile_image, (tile_size, tile_size)) In theory I dont need this

                if self.board[row][col] is not None:
                    piece_image = pygame.image.load(self.board[row][col].image)
                    piece_image = pygame.transform.scale(piece_image, (tile_size, tile_size))
                    tile_image.blit(piece_image, (0,0))

                # Calculate the position on the screen
                x_pos = col * tile_size
                y_pos = row * tile_size

                # Draw the tile on the screen at the calculated position
                screen.blit(tile_image, (x_pos, y_pos))