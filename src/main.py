import pygame
from src.Board import Board
from src.constants import tile_size, board_size, pieces, font, letters, numbers, margin, inverse_pieces, piece_creator
from src.Pieces.Pieces import *
import re
import threading


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

def evaluate_move(board, notation, color):
    """
    Evaluates a move given in algebraic notation.
    :param board: The Board object representing the current board state.
    :param notation: A string representing the move in algebraic notation (e.g., "Nf3", "e4", "O-O").
    :param color: The color of the player making the move ("white" or "black").
    :return: A tuple (is_valid, message), where `is_valid` is a boolean indicating if the move is valid, and `message` provides feedback.
    """
    # Regular expressions for parsing different types of moves
    piece_move = re.match(r"([KQRBN]?)([a-h]?[1-8]?)(x?)([a-h][1-8])(=?)([QRBN]?)([+#]?)", notation)
    castling_move = re.match(r"O-O(-O)?", notation)

    # Handle castling
    if castling_move:
        is_kingside = castling_move.group(1) is None
        if board.is_castling_valid(color, is_kingside):
            board.execute_castle(color, is_kingside)
            return True, f"{color.capitalize()} castled {'kingside' if is_kingside else 'queenside'}."
        else:
            return False, f"Invalid castling move for {color}."

    # Handle piece or pawn moves
    if piece_move:
        piece_symbol, disambiguation, take, target_square, promotion, promotion_piece, check = piece_move.groups()
        target_square = (target_square[0], int(target_square[1]))
        take = take == "x"
        
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
        result = piece.move(target_square, board, take=take)
        if result[0]: # The move executes only if it is valid
            # print(f"Previous: {prev}, Objective: {target_square}, piece pos: {piece.pos}")
            if result[1] == "En passant":
                board[get_en_passant_pos(target_square, color)] = None
            else:
                if result[1] == 'Two fowards':
                    board.last_pawn_move = target_square
                else: 
                    board.last_pawn_move = None
            board[prev] = None
            if promotion == "":
                piece = piece
            else:
                piece = piece_creator.create_piece(pieces[promotion_piece.lower()], color)
                piece.pos = target_square
            board[target_square] = piece
            return True, f"{color.capitalize()} {piece_type} moved to {target_square}{check}."
        else:
            return False, f"Invalid move for {color} {piece_type} to {target_square}."
    # If move format is not recognized
    return False, "Invalid or unrecognized move notation."

def get_en_passant_pos(target_square, color):
    direction = 1 if color == "b" else -1
    return (target_square[0], target_square[1] + direction)

def get_tile_from_click(position, board_size, tile_size, margin):
    """
    Convert click position (x, y) into the board tile (column, row).
    
    Parameters:
        x, y (int): Click coordinates.
        board_size (int): Number of squares per row or column (assumes a square board).
        tile_size (int): Size of each square in pixels.
        margin (int): Margin size around the board in pixels.

    Returns:
        (str, int): Position in chess notation, e.g., ('e', 4).
    """
    # Adjust coordinates to remove the margin
    x = position[0]
    y = position[1]
    adjusted_x = x - margin
    adjusted_y = y - margin

    # Check if the click is within the board boundaries
    board_pixel_size = board_size * tile_size
    if adjusted_x < 0 or adjusted_y < 0 or adjusted_x >= board_pixel_size or adjusted_y >= board_pixel_size:
        return None  # Click is outside the board

    # Calculate the column and row based on the adjusted coordinates
    col_index = adjusted_x // tile_size  # Integer division to get the column index
    row_index = adjusted_y // tile_size  # Integer division to get the row index

    # Convert to chess notation (e.g., ('e', 4))
    col_letter = chr(ord('a') + col_index)  # 'a' to 'h' for columns
    row_number = board_size - row_index     # '8' to '1' for rows (top to bottom)

    return (col_letter, row_number)

def is_capture(board, final_tile, current_piece_color, piece):
    """
    Checks if the move to `final_tile` is a capture.
    
    Parameters:
        board (dict or 2D array): The current board state.
        final_tile (tuple): The target position (e.g., ('e', 4)).
        current_piece_color (str): The color of the piece moving ('w' for white, 'b' for black).
        
    Returns:
        bool: True if the move is a capture, False otherwise.
    """
    # Get the piece at the final tile
    target_piece = board[(final_tile[0], final_tile[1])]  # Adjust based on your board structure

    # En passant
    if piece == "pawn":
        if target_piece is None and board.last_pawn_move == get_en_passant_pos(final_tile, current_piece_color):
            print("En passant")
            return True
    
    # If there is a piece at the final tile and it's of the opposite color, it's a capture
    if target_piece and target_piece.color != current_piece_color:
        return True
    return False

def convert_to_algebraic(initial_tile, final_tile, piece, is_capture=False, check="", disambiguation='', promotion=None):
    """
    Converts a move from initial_tile to final_tile into algebraic notation with minimal disambiguation, including castling and promotion.
    
    Parameters:
        initial_tile (tuple): Starting position in chess notation, e.g., ('e', 2).
        final_tile (tuple): Ending position in chess notation, e.g., ('e', 4).
        piece (str): The piece type, e.g., 'P' for pawn, 'K' for king, etc.
        is_capture (bool): Whether the move is a capture.
        is_check (bool): Whether the move puts the opponent in check.
        is_checkmate (bool): Whether the move puts the opponent in checkmate.
        disambiguation (str): Controls disambiguation - 'file', 'rank', or 'full' (both file and rank).
        promotion (str): The piece to which a pawn is promoted, e.g., 'Q' for queen.

    Returns:
        str: Move in algebraic notation.
    """
    # Check for castling if the piece is a king
    if piece == 'K' and abs(ord(final_tile[0]) - ord(initial_tile[0])) == 2:
        # Determine kingside or queenside castling based on target file
        if final_tile[0] > initial_tile[0]:
            return "O-O" + check
        else:
            return "O-O-O" + check
    
    final_pos = f"{final_tile[0]}{final_tile[1]}"
    
    # Piece symbol (empty for pawn moves)
    piece_symbol = inverse_pieces[piece].upper()
    
    # Capture notation
    capture_symbol = "x" if is_capture else ""
    
    # Check and checkmate notation
    end_symbol = check
    
    # Determine minimal disambiguation
    initial_file = initial_tile[0]
    initial_rank = initial_tile[1]
    initial_pos = ""
    
    if piece_symbol != "P":  # Only apply disambiguation for non-pawn moves
        if disambiguation == 'file':
            initial_pos = f"{initial_file}"
        elif disambiguation == 'rank':
            initial_pos = f"{initial_rank}"
        elif disambiguation == 'full':
            initial_pos = f"{initial_file}{initial_rank}"

    # Construct the move notation
    if piece_symbol == "P":  # Pawn moves have a special notation
        move_notation = f"{initial_file}{capture_symbol}{final_pos}" if is_capture else f"{final_pos}"
        # Add promotion notation if applicable
        if promotion:
            move_notation += f"={promotion.upper()}"
    else:
        move_notation = f"{piece_symbol}{initial_pos}{capture_symbol}{final_pos}"

    return f"{move_notation}{end_symbol}"

def get_promotion():
    """
    Prompts the user for the piece type they wish to promote to.
    Runs in a separate thread to avoid blocking the main program.
    """
    def request_promotion():
        # Ask user for promotion type
        while True:
            type_requested = input("Promote pawn to (Q, R, B, N): ").strip().upper()
            if type_requested in {'Q', 'R', 'B', 'N'}:
                promotion_result.append(type_requested)
                break
            else:
                print("Invalid choice. Please choose from Q, R, B, or N.")

    # List to store promotion result to be accessed outside the thread
    promotion_result = []
    
    # Start a thread for user input
    promotion_thread = threading.Thread(target=request_promotion)
    promotion_thread.start()
    
    # Wait for the thread to complete
    promotion_thread.join()
    
    # Return the promotion result
    return promotion_result[0] if promotion_result else None

def is_promotion_needed(final_tile, color, piece_type):
    """
    Determines if a promotion is needed based on the piece's position and type.
    
    Parameters:
        board: The current game board.
        final_tile (tuple): The final position in chess notation (e.g., ('e', 8)).
        color (str): The color of the piece ('w' for white, 'b' for black).
        piece_type (str): The type of the piece (should be 'pawn' to consider promotion).

    Returns:
        bool: True if promotion is needed, False otherwise.
    """
    # Check if the piece is a pawn
    if piece_type.lower() != "pawn":
        return None

    # Determine the promotion row based on color
    promotion_row = 8 if color == 'w' else 1

    # Check if the pawn has reached the promotion rank
    if final_tile[1] == promotion_row:
        return True

    return None

def is_check_needed(board, initial_tile, final_tile, piece, color):
    """
    Determines if a move results in a check or checkmate on the opponent's king.

    Parameters:
        board (Board): The chess board instance.
        initial_tile (tuple): Starting position in chess notation (e.g., ('e', 2)).
        final_tile (tuple): Ending position in chess notation (e.g., ('e', 4)).
        piece (Piece): The piece being moved.
        promotion (str): The piece type to which a pawn is promoted (e.g., 'Q'), or None if no promotion.
        capture (bool): True if the move is a capture, False otherwise.
        color (str): The color of the player making the move ('w' or 'b').
        piece_type (str): The type of the piece being moved.

    Returns:
        str: "checkmate" if the move results in checkmate, "check" if it results in a check, or "" if neither.
    """
    opponent_color = "b" if color == "w" else "w"

    # Temporarily execute the move
    original_piece = board[final_tile]
    board[final_tile] = piece
    board[initial_tile] = None
    piece.pos = final_tile  # Update the piece's position

    # Locate the opponent's king
    king_position = None
    for row in range(8):
        for col in range(8):
            current_piece = board[(chr(col + ord('a')), row + 1)]
            if current_piece and current_piece.color == opponent_color and current_piece.type == 'king':
                king_position = (chr(col + ord('a')), row + 1)
                break
        if king_position:
            break

    # Check if the opponent's king is now under attack
    is_check = board.is_square_under_attack(king_position, color) if king_position else False

    # Determine if it's checkmate
    is_checkmate = False
    if is_check:
        # Check if the opponent's king has any legal moves to escape check
        is_checkmate = True  # Assume checkmate until proven otherwise
        for row in range(8):
            for col in range(8):
                square = (chr(col + ord('a')), row + 1)
                # Check all possible moves of the opponent's king
                if king_position and board.is_square_under_attack(square, color) is False:
                    is_checkmate = False
                    break

    # Undo the temporary move
    board[initial_tile] = piece
    board[final_tile] = original_piece
    piece.pos = initial_tile  # Restore the piece's original position

    if is_checkmate:
        return "#"
    elif is_check:
        return "+"
    else:
        return ""

def get_disambiguation(board, initial_tile, final_tile, piece, capture):
    """
    Determines the minimal disambiguation required for a move.
    
    Parameters:
        board (dict): The current board state with positions as keys and piece objects as values.
        initial_tile (tuple): Starting position in chess notation, e.g., ('e', 2).
        final_tile (tuple): Ending position in chess notation, e.g., ('e', 4).
        piece (str): The piece symbol, e.g., 'N' for knight, 'R' for rook.

    Returns:
        str: 'file' if only the file is needed, 'rank' if only the rank is needed, 'full' if both are needed, or '' if no disambiguation is needed.
    """
    initial_file, initial_rank = initial_tile
    initial_rank = int(initial_rank)

    # Find all pieces of the same type and color that could move to final_tile
    print(capture)
    candidates = [
        pos for pos, other_piece in board.items()
        if other_piece and other_piece.type == piece and other_piece.color == board[initial_tile].color
        and other_piece.is_move_valid(final_tile, board, capture)  # Assume a method can_move_to exists for the piece
    ]
    print(candidates)
    # If no other pieces can move to the final tile, no disambiguation is needed
    if len(candidates) == 1:
        return ''

    # Check if disambiguation by file or rank alone is sufficient
    same_file = [pos for pos in candidates if pos[0] == initial_file]
    same_rank = [pos for pos in candidates if int(pos[1]) == initial_rank]

    if len(same_file) == 1:
        return 'file'  # Only file needed to distinguish this move
    elif len(same_rank) == 1:
        return 'rank'  # Only rank needed to distinguish this move
    else:
        return 'full'  # Both file and rank are needed for disambiguation

def move_execution(board, initial_tile, final_tile, turn):
    turns = ["w", "b"]
    color = turns[turn]
    piece = board[initial_tile]
    piece_type = piece.type
    promotion = is_promotion_needed(final_tile, color, piece_type)
    if promotion:
        promotion = get_promotion()
    capture = is_capture(board, final_tile,  color, piece_type)
    check = is_check_needed(board, initial_tile, final_tile, piece, color)
    print(check)
    move = convert_to_algebraic(initial_tile, final_tile, piece_type, capture, check, promotion=promotion)
    print(move)
    result = evaluate_move(board, move, color)
    # print(move, result)
    if result[1] == "Move is ambiguous; specify which piece to move.":
        disambiguation = get_disambiguation(board, initial_tile, final_tile, piece_type, capture)
        move = convert_to_algebraic(initial_tile, final_tile, piece_type, capture, check, disambiguation, promotion=promotion)
        result = evaluate_move(board, move, color)
    if result[0]:
        turn = 1-turn
    return turn

def click_logic(click, board, event, board_size, tile_size, margin, turn, initial_tile=None, ):
    click = (click + 1) % 3
    pos = event.pos
    tile = get_tile_from_click(pos, board_size, tile_size, margin)

    if click == 1:
        # First click: Select a piece
        if tile is None or board[tile] is None:
            click = 0  # Reset if no valid piece is selected
        else:
            initial_tile = tile

    elif click == 2:
        # Second click: Move the piece
        if tile is not None:
            turn = move_execution(board, initial_tile, tile, turn)
        click = 0  # Reset click after attempting a move

    return click, initial_tile, turn

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((tile_size*board_size + 2*margin, tile_size*board_size + 2*margin), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    running = True

    board = Board()
    board.initialize_board()

    click = 0
    initial_tile = None
    turn = 0

    while running:
        # poll for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    click, initial_tile, turn = click_logic(click, board, event, board_size, tile_size, margin, turn, initial_tile)
        
        screen.fill("gray")
        display()
        board.draw(screen)

        pygame.display.flip()

        clock.tick(20)
    pygame.quit()