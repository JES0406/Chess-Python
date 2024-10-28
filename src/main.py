import pygame
from src.Board import Board
from src.constants import tile_size, board_size
import time


import re

def evaluate_move(board, notation, color):
    """
    Evaluates a move given in algebraic notation.
    :param board: The Board object representing the current board state.
    :param notation: A string representing the move in algebraic notation (e.g., "Nf3", "e4", "O-O").
    :param color: The color of the player making the move ("white" or "black").
    :return: A tuple (is_valid, message), where `is_valid` is a boolean indicating if the move is valid, and `message` provides feedback.
    """
    # Regular expressions for parsing different types of moves
    piece_move = re.match(r"([KQRBN]?)([a-h]?[1-8]?)x?([a-h][1-8])([+#]?)", notation)
    castling_move = re.match(r"O-O(-O)?", notation)
    pawn_move = re.match(r"([a-h])([1-8])", notation)

    # Handle castling
    if castling_move:
        is_kingside = castling_move.group(1) is None
        if board.is_castling_valid(color, kingside=is_kingside):
            return True, f"{color.capitalize()} castled {'kingside' if is_kingside else 'queenside'}."
        else:
            return False, f"Invalid castling move for {color}."

    # Handle piece or pawn moves
    if piece_move:
        piece_symbol, disambiguation, target_square, check = piece_move.groups()
        
        # Determine piece type; if empty, it's a pawn move
        piece_type = "pawn" if piece_symbol == "" else piece_symbol.lower()
        target_col, target_row = target_square[0], int(target_square[1])

        # Find the piece based on the color, piece type, and target position
        possible_pieces = board.find_pieces(color=color, piece_type=piece_type, target_square=target_square, disambiguation=disambiguation)
        
        if not possible_pieces:
            return False, f"No valid {piece_type} found for {color} that can move to {target_square}."
        if len(possible_pieces) > 1:
            return False, "Move is ambiguous; specify which piece to move."

        # Validate the move for the found piece
        piece = possible_pieces[0]
        if piece.move(target_square): # The move executes only if it is valid
            return True, f"{color.capitalize()} {piece_type} moved to {target_square}{check}."
        else:
            return False, f"Invalid move for {color} {piece_type} to {target_square}."

    # Handle simple pawn moves without captures
    if pawn_move:
        target_col, target_row = pawn_move.groups()
        if board.is_move_valid_for_pawn(color, target_col, int(target_row)):
            return True, f"{color.capitalize()} pawn moved to {target_col}{target_row}."
        else:
            return False, f"Invalid move for {color} pawn to {target_col}{target_row}."

    # If move format is not recognized
    return False, "Invalid or unrecognized move notation."


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((tile_size*board_size, tile_size*board_size), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    running = True

    board = Board()
    board.initialize_board()

    try:
        while running:
            # poll for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            screen.fill("black")

            board.draw(screen)

            pygame.display.flip()

            # move = input()
            # print(evaluate_move(board, move, "w"))


            clock.tick(20)
        pygame.quit()
    except Exception as e:
        print(e)
        time.sleep(1)
        pygame.quit()