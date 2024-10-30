from src.constants import board_size, font, tile_size, letters, numbers, pieces, piece_creator, inverse_pieces
import re
from src.utils import get_en_passant_pos

def evaluate_move(board, notation, color):
    """
    Evaluates a move given in algebraic notation.
    """
    # Determine the move type (castling, standard move, etc.)
    if is_castling(notation):
        return handle_castling(board, notation, color)

    piece_data = parse_notation(notation)
    if piece_data:
        return handle_piece_move(board, color, **piece_data)

    return False, "Invalid or unrecognized move notation."


def is_castling(notation):
    return re.match(r"O-O(-O)?", notation)


def handle_castling(board, notation, color):
    """
    Handles castling moves.
    """
    is_kingside = notation == "O-O"
    if board.is_castling_valid(color, is_kingside):
        board.execute_castle(color, is_kingside)
        return True, f"{color.capitalize()} castled {'kingside' if is_kingside else 'queenside'}."
    return False, f"Invalid castling move for {color}."


def parse_notation(notation):
    """
    Parses the algebraic notation and returns a dictionary with move components.
    """
    match = re.match(r"([KQRBN]?)([a-h]?[1-8]?)(x?)([a-h][1-8])(=?)([QRBN]?)([+#]?)", notation)
    if match:
        piece_symbol, disambiguation, take, target_square, _, promotion_piece, check = match.groups()
        return {
            "piece_symbol": piece_symbol,
            "disambiguation": disambiguation,
            "take": take == "x",
            "target_square": (target_square[0], int(target_square[1])),
            "promotion_piece": promotion_piece,
            "check": check
        }
    return None


def handle_piece_move(board, color, piece_symbol, disambiguation, take, target_square, promotion_piece, check):
    """
    Handles standard piece and pawn moves, including en passant and promotion.
    """
    piece_type = "p" if piece_symbol == "" else piece_symbol.lower()
    piece_type = pieces[piece_type]
    possible_pieces = find_piece_to_move(board, color, piece_type, target_square, disambiguation, take)

    if not possible_pieces:
        return False, f"No valid {piece_type} found for {color} that can move to {target_square}."
    if len(possible_pieces) > 1:
        return False, "Move is ambiguous; specify which piece to move."

    piece = possible_pieces[0]
    prev_pos = piece.pos
    move_result, message = piece.move(target_square, board, take=take)

    if move_result:
        finalize_move(board, piece, target_square, message, promotion_piece, color, prev_pos)
        return True, f"{color.capitalize()} {piece_type} moved to {target_square}{check}."
    
    return False, f"Invalid move for {color} {piece_type} to {target_square}."


def find_piece_to_move(board, color, piece_type, target_square, disambiguation, take):
    """
    Finds possible pieces of the specified type and color that can move to the target square.
    """
    return board.find_pieces(color=color, piece_type=piece_type, target_square=target_square,
                             disambiguation=disambiguation, take=take)



def finalize_move(board, piece, target_square, message, promotion_piece, color, prev_pos):
    """
    Finalizes the move on the board, handling en passant, promotion, and board updates.
    """
    if message == "En passant":
        en_passant_pos = get_en_passant_pos(target_square, color)
        board[en_passant_pos] = None  # Remove captured pawn

    # Handle two-square pawn move tracking
    board.last_pawn_move = target_square if message == "Two forwards" else None

    board[prev_pos] = None
    # Handle promotion if needed
    if promotion_piece:
        piece = piece_creator.create_piece(pieces[promotion_piece.lower()], color)
    piece.pos = target_square

    # Update the board with the new piece position
    board[target_square] = piece