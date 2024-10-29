import pygame
from src.Board import Board
from src.constants import tile_size, board_size, pieces, font, letters, numbers
import time
import re
import threading

def evaluate_move(board, notation, color):
    """
    Evaluates a move given in algebraic notation.
    :param board: The Board object representing the current board state.
    :param notation: A string representing the move in algebraic notation (e.g., "Nf3", "e4", "O-O").
    :param color: The color of the player making the move ("white" or "black").
    :return: A tuple (is_valid, message), where `is_valid` is a boolean indicating if the move is valid, and `message` provides feedback.
    """
    # Regular expressions for parsing different types of moves
    piece_move = re.match(r"([KQRBN]?)([a-h]?[1-8]?)(x?)([a-h][1-8])([+#]?)", notation)
    castling_move = re.match(r"O-O(-O)?", notation)

    # Handle castling
    if castling_move:
        is_kingside = castling_move.group(1) is None
        if board.is_castling_valid(color, kingside=is_kingside):
            return True, f"{color.capitalize()} castled {'kingside' if is_kingside else 'queenside'}."
        else:
            return False, f"Invalid castling move for {color}."

    # Handle piece or pawn moves
    if piece_move:
        piece_symbol, disambiguation, take, target_square, check = piece_move.groups()
        # print(piece_move.groups())
        target_square = (target_square[0], int(target_square[1]))
        
        # Determine piece type; if empty, it's a pawn move
        piece_type = "p" if piece_symbol == "" else piece_symbol.lower()
        piece_type = pieces[piece_type]
        # Find the piece based on the color, piece type, and target position
        possible_pieces = board.find_pieces(color=color, piece_type=piece_type, target_square=target_square, disambiguation=disambiguation, take=take)
        if not possible_pieces:
            return False, f"No valid {piece_type} found for {color} that can move to {target_square}."
        if len(possible_pieces) > 1:
            return False, "Move is ambiguous; specify which piece to move."

        # Validate the move for the found piece
        piece = possible_pieces[0]
        prev = piece.pos
        if piece.move(target_square, board.board, take=take): # The move executes only if it is valid
            # print(f"Previous: {prev}, Objective: {target_square}, piece pos: {piece.pos}")
            board[prev] = None
            board[target_square] = piece
            return True, f"{color.capitalize()} {piece_type} moved to {target_square}{check}."
        else:
            return False, f"Invalid move for {color} {piece_type} to {target_square}."
    # If move format is not recognized
    return False, "Invalid or unrecognized move notation."

def display():
    for col in range(board_size):
        letter = font.render(letters[col], True, 'black')  # Render in black color
        x_pos = col * tile_size + tile_size // 2

        # Bottom of the board
        screen.blit(letter, (x_pos, 0))

    # Draw row labels (1-8) on the left and right sides
    for row in range(board_size):
        number = font.render(str(numbers[7 - row]), True, (0, 0, 0))  # Render in black color
        y_pos = row * tile_size + tile_size // 2

        # Left of the board
        screen.blit(number, (0, y_pos))

def move_execution():
    global move, running
    turns = ["w", "b"]
    turn = 0
    while running:
        move = input("Move: ")
        result = evaluate_move(board, move, turns[turn])
        print(result[1])
        if result[0]:
            turn = 1-turn

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((tile_size*board_size + 50, tile_size*board_size + 50), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    running = True

    board = Board()
    board.initialize_board()

    print(board[("a", 8)])

    move = ""

    thread = threading.Thread(target=move_execution)
    thread.start()

    try:
        while running:
            # poll for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            screen.fill("gray")
            display()
            board.draw(screen)

            pygame.display.flip()

            clock.tick(20)
        thread.join()
        pygame.quit()
    except Exception as e:
        print(e)
        time.sleep(1)
        running = False
        thread.join()
        pygame.quit()