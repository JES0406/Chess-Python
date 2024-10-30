from src.constants import inverse_pieces
import threading
from src.utils import get_en_passant_pos
from src.moving_logic import evaluate_move

def is_capture(board, final_tile, current_piece_color, piece_type):
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
    if piece_type == "pawn":
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
    if piece == 'king' and abs(ord(final_tile[0]) - ord(initial_tile[0])) == 2:
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

def get_promotion(final_tyle, color, piece_type):
    """
    Prompts the user for the piece type they wish to promote to.
    Runs in a separate thread to avoid blocking the main program.
    """
    if is_promotion_needed:
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
    return False

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
    """
    opponent_color = "b" if color == "w" else "w"

    # Temporarily execute the move
    original_piece = execute_temporary_move(board, initial_tile, final_tile, piece)

    # Locate the opponent's king
    king_position = find_king_position(board, opponent_color)

    # Check if the opponent's king is now under attack
    is_check = board.is_square_under_attack(king_position, color) if king_position else False

    # Determine if it's checkmate
    print(can_escape_check(board, opponent_color, king_position))
    is_checkmate = is_check and not can_escape_check(board, opponent_color, king_position)

    # Undo the temporary move
    undo_temporary_move(board, initial_tile, final_tile, piece, original_piece)

    # Return check status
    return "#" if is_checkmate else "+" if is_check else ""


def execute_temporary_move(board, initial_tile, final_tile, piece):
    """
    Executes a temporary move on the board and returns the piece displaced by the move.
    """
    original_piece = board[final_tile]
    board[final_tile] = piece
    board[initial_tile] = None
    piece.pos = final_tile  # Update piece position
    return original_piece


def undo_temporary_move(board, initial_tile, final_tile, piece, original_piece):
    """
    Reverts a temporary move on the board.
    """
    board[initial_tile] = piece
    board[final_tile] = original_piece
    piece.pos = initial_tile  # Restore piece position


def find_king_position(board, color):
    """
    Finds and returns the position of the king of a given color.
    """
    for row in range(8):
        for col in range(8):
            piece = board[(chr(col + ord('a')), row + 1)]
            if piece and piece.color == color and piece.type == 'king':
                return (chr(col + ord('a')), row + 1)
    return None


def can_escape_check(board, color, king_position):
    """
    Checks if there is any legal move that can remove the check on the king.
    First checks if the king can escape, then if an attacking piece can be captured,
    and finally if the check can be blocked by other pieces.

    Parameters:
        board (Board): The current board instance.
        color (str): The color of the pieces to check ('w' for white, 'b' for black).
        king_position (tuple): The position of the king in (file, rank) format (e.g., ('e', 1)).

    Returns:
        bool: True if any move can escape check, False if none can.
    """
    # Step 1: Check if the king can escape by moving to a safe adjacent square
    if can_king_escape(board, color, king_position):
        return True

    # Step 2: Check if an attacking piece can be captured
    attackers = get_attackers(board, color, king_position)
    if can_capture_attacker(board, color, attackers):
        return True

    # Step 3: Check if any piece can block the check
    if can_block_check(board, color, king_position, attackers):
        return True

    # No move could evade the check
    return False


def can_king_escape(board, color, king_position):
    """
    Checks if the king can escape check by moving to any adjacent square.
    """
    king_moves = get_legal_moves(board, king_position)  # Get all legal moves for the king
    for move in king_moves:
        if not board.is_square_under_attack(move, color):
            return True
    return False


def get_attackers(board, color, king_position):
    """
    Returns a list of positions of all pieces currently attacking the king.
    """
    opponent_color = "b" if color == "w" else "w"
    attackers = []
    for row in range(8):
        for col in range(8):
            pos = (chr(col + ord('a')), row + 1)
            piece = board[pos]
            if piece and piece.color == opponent_color:
                if piece.is_move_valid(king_position, board, take=True)[0]:
                    attackers.append(pos)
    return attackers


def can_capture_attacker(board, color, attackers):
    """
    Checks if any piece can capture an attacker to remove the check.
    """
    for attacker_pos in attackers:
        for row in range(8):
            for col in range(8):
                piece_pos = (chr(col + ord('a')), row + 1)
                piece = board[piece_pos]
                if piece and piece.color == color and piece.type != "king":
                    if piece.is_move_valid(attacker_pos, board, take=True)[0]:
                        print(piece)
                        # Simulate the capture and check if it removes the check
                        original_piece = execute_temporary_move(board, piece_pos, attacker_pos, piece)
                        king_position = find_king_position(board, color)
                        king_safe = not board.is_square_under_attack(king_position, color)
                        undo_temporary_move(board, piece_pos, attacker_pos, piece, original_piece)

                        if king_safe:
                            return True
    return False


def can_block_check(board, color, king_position, attackers):
    """
    Checks if any piece can block the check by moving between the king and the attacker.
    Only applicable if there is a single sliding attacker (rook, bishop, or queen).
    """
    if len(attackers) != 1:
        return False  # Only one attacker can be blocked; otherwise, it's double check

    attacker_pos = attackers[0]
    attacker_piece = board[attacker_pos]

    # Check if the attacker is a sliding piece that can be blocked
    if attacker_piece.type not in ["rook", "bishop", "queen"]:
        return False  # Non-sliding pieces can't be blocked

    # Generate all squares between the attacker and the king
    blocking_squares = get_squares_between(king_position, attacker_pos)

    # Check if any piece of the same color can move to a blocking square
    for square in blocking_squares:
        for row in range(8):
            for col in range(8):
                piece_pos = (chr(col + ord('a')), row + 1)
                piece = board[piece_pos]
                if piece and piece.color == color:
                    if piece.is_move_valid(square, board, take=False)[0]:
                        # Simulate the block and check if it removes the check
                        original_piece = execute_temporary_move(board, piece_pos, square, piece)
                        king_safe = not board.is_square_under_attack(king_position, color)
                        undo_temporary_move(board, piece_pos, square, piece, original_piece)

                        if king_safe:
                            return True
    return False


def get_squares_between(start, end):
    """
    Returns all squares between two positions (start and end) in a straight line or diagonal.
    Only used for sliding pieces (rook, bishop, queen).
    """
    squares_between = []

    file_diff = ord(end[0]) - ord(start[0])
    rank_diff = end[1] - start[1]

    # Determine the direction of movement
    file_step = (file_diff // abs(file_diff)) if file_diff != 0 else 0
    rank_step = (rank_diff // abs(rank_diff)) if rank_diff != 0 else 0

    # Start at the first square after the starting square and move towards the end square
    current_file = ord(start[0]) + file_step
    current_rank = start[1] + rank_step

    while (current_file, current_rank) != (ord(end[0]), end[1]):
        squares_between.append((chr(current_file), current_rank))
        current_file += file_step
        current_rank += rank_step

    return squares_between


def get_legal_moves(board, position):
    """
    Returns all legal moves for the piece at the given position.
    
    Parameters:
        board (Board): The current board instance.
        position (tuple): The position (file, rank) of the piece (e.g., ('e', 4)).
    
    Returns:
        list: A list of legal moves in algebraic notation, or empty list if no piece is found.
    """
    piece = board[position]
    if not piece:
        return []  # No piece at the given position

    legal_moves = []
    original_pos = piece.pos

    # Loop over all possible target squares on an 8x8 board
    for target_row in range(1, 9):
        for target_col in range(8):
            target_square = (chr(target_col + ord('a')), target_row)

            # Skip if the target is the same as the current position
            if position == target_square:
                continue

            # Check if the move is valid for this piece type
            is_valid_move, move_type = piece.is_move_valid(target_square, board, take=(board[target_square] is not None))
            if is_valid_move:
                # Simulate the move and check if it leaves the king in check
                original_target_piece = board[target_square]
                board[target_square] = piece
                board[original_pos] = None
                piece.pos = target_square

                # Check if this move would leave the king safe
                king_position = find_king_position(board, piece.color)
                king_safe = not board.is_square_under_attack(king_position, piece.color)

                # Undo the move
                board[original_pos] = piece
                board[target_square] = original_target_piece
                piece.pos = original_pos

                # If the king is safe, add the move to the list of legal moves
                if king_safe:
                    legal_moves.append(target_square)

    return legal_moves

def get_disambiguation(board, initial_tile, final_tile, piece, capture):
    """
    Determines the minimal disambiguation required for a move.
    """
    initial_file, initial_rank = initial_tile
    initial_rank = int(initial_rank)

    # Find all possible pieces that could move to final_tile
    candidates = find_candidates(board, initial_tile, final_tile, piece, capture)
    
    # Check if disambiguation is needed
    if not needs_disambiguation(candidates):
        return ''  # No disambiguation needed

    # Determine the minimal disambiguation type (file, rank, or full)
    return get_disambiguation_type(candidates, initial_file, initial_rank)


def find_candidates(board, initial_tile, final_tile, piece, capture):
    """
    Finds all pieces of the same type and color that could move to the final tile.
    """
    color = board[initial_tile].color
    return [
        pos for pos, other_piece in board.items()
        if other_piece and other_piece.type == piece and other_piece.color == color
        and other_piece.is_move_valid(final_tile, board, capture)
    ]


def needs_disambiguation(candidates):
    """
    Checks if multiple pieces can move to the target tile, requiring disambiguation.
    """
    return len(candidates) > 1


def get_disambiguation_type(candidates, initial_file, initial_rank):
    """
    Determines if the disambiguation is needed by file, rank, or both.
    """
    same_file = [pos for pos in candidates if pos[0] == initial_file]
    same_rank = [pos for pos in candidates if int(pos[1]) == initial_rank]

    if len(same_file) == 1:
        return 'file'  # Only file needed to distinguish this move
    elif len(same_rank) == 1:
        return 'rank'  # Only rank needed to distinguish this move
    return 'full'  # Both file and rank are needed for disambiguation


def move_execution(board, initial_tile, final_tile, turn):
    """
    Executes a move, evaluates it, and updates the turn if valid.
    """
    color = get_turn_color(turn)
    piece = board[initial_tile]
    move_data = prepare_move_data(board, initial_tile, final_tile, piece, color)

    # Convert the move to algebraic notation and evaluate it
    move = convert_to_algebraic(initial_tile, final_tile, piece.type, move_data["capture"], move_data["check"], promotion=move_data["promotion"])
    print(move)
    result = evaluate_move(board, move, color)

    # Handle disambiguation if needed
    if result[1] == "Move is ambiguous; specify which piece to move.":
        move = resolve_disambiguation(board, initial_tile, final_tile, piece.type, move_data)
        result = evaluate_move(board, move, color)

    # Update turn and check for victory
    if result[0]:
        turn = 1 - turn
    check_for_victory(move_data["check"], color)
    
    return turn

def get_move(board, initial_tile, final_tile, piece, piece_color):
    move_data = prepare_move_data(board, initial_tile, final_tile, piece, piece_color)

    # Convert the move to algebraic notation and evaluate it
    return convert_to_algebraic(initial_tile, final_tile, piece.type, move_data["capture"], move_data["check"], promotion=move_data["promotion"])
def get_turn_color(turn):
    """
    Returns the color based on the turn index.
    """
    return "w" if turn == 0 else "b"


def prepare_move_data(board, initial_tile, final_tile, piece, color):
    """
    Prepares data for the move, including promotion, capture, and check status.
    """
    piece_type = piece.type
    promotion = get_promotion() if is_promotion_needed(final_tile, color, piece_type) else None
    capture = is_capture(board, final_tile, color, piece_type)
    check = is_check_needed(board, initial_tile, final_tile, piece, color)
    
    return {
        "promotion": promotion,
        "capture": capture,
        "check": check
    }


def resolve_disambiguation(board, initial_tile, final_tile, piece_type, move_data):
    """
    Resolves disambiguation if multiple pieces could make the same move.
    """
    disambiguation = get_disambiguation(board, initial_tile, final_tile, piece_type, move_data["capture"])
    return convert_to_algebraic(initial_tile, final_tile, piece_type, move_data["capture"], move_data["check"], disambiguation, promotion=move_data["promotion"])


def check_for_victory(check, color):
    """
    Checks if the move results in a checkmate and raises a VictoryEvent if true.
    """
    if check == "#":
        # raise VictoryEvent(f"{color} has won")
        pass


def click_logic(click, board, event, board_size, tile_size, margin, turn, initial_tile=None):
    """
    Handles the logic for piece selection and movement based on mouse clicks.
    """
    click = increment_click(click)
    tile = get_selected_tile(event, board_size, tile_size, margin)

    if click == 1:
        click, initial_tile = select_tile(click, board, tile)
    elif click == 2:
        click, turn = attempt_move(click, board, initial_tile, tile, turn)

    return click, initial_tile, turn


def increment_click(click):
    """
    Increments and wraps the click state (1 or 2) based on the current state.
    """
    return (click + 1) % 3


def get_selected_tile(event, board_size, tile_size, margin):
    """
    Converts the mouse click position to a tile on the board.
    """
    pos = event.pos
    return get_tile_from_click(pos, board_size, tile_size, margin)


def select_tile(click, board, tile):
    """
    Handles the logic for the first click, selecting a piece on the board.
    Resets the click if no piece is selected.
    """
    if tile is None or board[tile] is None:
        click = 0  # Reset if no valid piece is selected
        return click, None
    return click, tile


def attempt_move(click, board, initial_tile, target_tile, turn):
    """
    Handles the logic for the second click, attempting to move the selected piece.
    """
    if target_tile is not None:
        turn = move_execution(board, initial_tile, target_tile, turn)
    click = 0  # Reset click after attempting a move
    return click, turn