from typing import Any
from src.constants import numbers, letters, tile_size, board_size, theme, font, margin, piece_creator
from src.Pieces.King import King
from src.Pieces.Rook import Rook
import pygame

class Board:
    def __init__(self) -> None:
        self._board = [[None for i in range(len(numbers))] for j in range(len(letters))]
        self.last_pawn_move = None # Track the last pawn move for en passant
        self.initialize_board()

    @property
    def board(self):
        return self._board
    
    def initialize_board(self):
        piece_order = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
        for col in range(board_size):
            for color, pawn_rank, main_rank in [('w', 2, 1), ('b', 7, 8)]:
                # Place pawns
                pawn = piece_creator.create_piece("pawn", color)
                pawn.pos = (letters[col], pawn_rank)
                self[(letters[col], pawn_rank)] = pawn

                # Place main pieces
                piece = piece_creator.create_piece(piece_order[col], color)
                piece.pos = (letters[col], main_rank)
                self[(letters[col], main_rank)] = piece

    def find_pieces(self, color, piece_type, target_square, disambiguation="", take = None):
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
                valid = piece.is_move_valid(target_square, self, take)
                if valid[0]:
                    # If disambiguation is provided, check if it matches
                    if disambiguation:
                        # Separate file and rank components if both are provided (e.g., "e2")
                        dis_file = disambiguation[0] if disambiguation[0] in letters else ""
                        dis_rank = disambiguation[1] if len(disambiguation) == 2 else disambiguation if disambiguation.isdigit() else ""

                        # Check if disambiguation file matches the piece's current file
                        if dis_file and piece.pos[0] != dis_file:
                            continue

                        # Check if disambiguation rank matches the piece's current rank
                        if dis_rank and str(piece.pos[1]) != dis_rank:
                            continue
                    
                    # Add the piece to the list of possible pieces
                    possible_pieces.append(piece)

        return possible_pieces
    
    def execute_castle(self, color, kingside):
        # Set starting positions based on color
        row = 1 if color == 'w' else 8
        king_start = ('e', row)
        king_end = ('g', row) if kingside else ('c', row)
        rook_start = ('h', row) if kingside else ('a', row)
        rook_end = ('f', row) if kingside else ('d', row)
        
        # Move the king to its castled position
        self[king_end] = self[king_start]
        self[king_start] = None  # Clear the king's starting position

        # Move the rook to its castled position
        self[rook_end] = self[rook_start]
        self[rook_start] = None  # Clear the rook's starting position


    def is_castling_valid(self, color, kingside):
        row = 1 if color == "w" else 8
        king_col = 4
        rook_col = 7 if kingside else 0
        step = 1 if kingside else -1
        king_file = chr(king_col + ord('a'))
        rook_file = chr(rook_col + ord('a'))

        # Retrieve the king and rook
        king = self[(king_file, row)]
        rook = self[(rook_file, row)]

        # Check if the king and rook are in the correct positions and are of the correct color
        if not isinstance(king, King) or king.color != color or king.has_moved:
            return False
        if not isinstance(rook, Rook) or rook.color != color or rook.has_moved:
            return False

        # Check path between king and rook for any blocking pieces
        for col in range(king_col + step, rook_col, step):
            position = (chr(col + ord('a')), row)  # Convert to chess notation
            if self[position] is not None:
                return False

        # Check that no square the king moves through (including starting and ending) is under attack
        for col in range(king_col, king_col + 2 * step, step):
            position = (chr(col + ord('a')), row)  # Convert to chess notation
            if self.is_square_under_attack(position, color):
                return False

        # If all conditions are satisfied, castling is valid
        return True
    
    def is_square_under_attack(self, square, attack_color):
        """
        Checks if a square is under attack by the opponent.
        :param square: Tuple (row, col) of the square to check.
        :param color: The color of the player making the check (used to identify opponent).
        :return: True if the square is under attack, False otherwise.
        """

        # Check if any opponent piece can move to the square
        defending_color = "b" if attack_color == "w" else "w"
        # Check if any opponent piece can legally move to the square
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece is not None and piece.color == attack_color:
                    # Check both capturing and non-capturing moves
                    is_valid_capture = piece.is_move_valid(square, self, take=True)[0]
                    if is_valid_capture or piece.is_move_valid(square, self, take=False)[0]:
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
                x_pos = col * tile_size + margin
                y_pos = (7 - row) * tile_size + margin  # Adjust for bottom-to-top display
                screen.blit(tile_image, (x_pos, y_pos))

    def __getitem__(self, item):
        return self.board[item[1]-1][ord(item[0]) - ord('a')]
    
    def __setitem__(self, key, value):
        # print("changes", key, value)
        self.board[key[1]-1][ord(key[0]) - ord('a')] = value

    def items(self):
        """
        Returns an iterator of positions and their contents in chess notation.
        """
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                # Convert matrix indices to chess notation
                file = chr(col + ord('a'))
                rank = row + 1
                yield (file, rank), piece
