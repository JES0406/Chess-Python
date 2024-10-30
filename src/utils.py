from src.constants import board_size, font, tile_size, letters, numbers, pieces, piece_creator, inverse_pieces, margin

def display(screen):
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

def get_en_passant_pos(target_square, color):
    direction = 1 if color == "b" else -1
    return (target_square[0], target_square[1] + direction)

def get_tile_from_click(position):
    """
    Convert click position (x, y) into the board tile (column, row) in chess notation.
    
    Parameters:
        position (tuple): Click coordinates (x, y).
        board_size (int): Number of squares per row or column (assumes a square board).
        tile_size (int): Size of each square in pixels.
        margin (int): Margin size around the board in pixels.

    Returns:
        (str, int): Position in chess notation, e.g., ('e', 4), or None if click is outside the board.
    """
    # Adjust coordinates to remove the margin
    adjusted_x, adjusted_y = adjust_coordinates_for_margin(position, margin)

    # Check if the click is within the board boundaries
    if not is_within_board_boundaries(adjusted_x, adjusted_y, board_size, tile_size):
        return None  # Click is outside the board

    # Calculate the column and row based on the adjusted coordinates
    col_index, row_index = calculate_board_indices(adjusted_x, adjusted_y, tile_size)

    # Convert indices to chess notation (e.g., ('e', 4))
    return convert_indices_to_chess_notation(col_index, row_index, board_size)


def adjust_coordinates_for_margin(position, margin):
    """
    Adjusts the click position to account for the margin around the board.
    
    Parameters:
        position (tuple): Original click coordinates (x, y).
        margin (int): Margin size around the board in pixels.
    
    Returns:
        (int, int): Adjusted coordinates.
    """
    x, y = position
    return x - margin, y - margin


def is_within_board_boundaries(x, y, board_size, tile_size):
    """
    Checks if the adjusted coordinates are within the board boundaries.
    
    Parameters:
        x, y (int): Adjusted click coordinates.
        board_size (int): Number of squares per row or column.
        tile_size (int): Size of each square in pixels.
    
    Returns:
        bool: True if within board boundaries, False otherwise.
    """
    board_pixel_size = board_size * tile_size
    return 0 <= x < board_pixel_size and 0 <= y < board_pixel_size


def calculate_board_indices(x, y, tile_size):
    """
    Calculates the column and row indices on the board based on adjusted coordinates.
    
    Parameters:
        x, y (int): Adjusted click coordinates.
        tile_size (int): Size of each square in pixels.
    
    Returns:
        (int, int): Column and row indices.
    """
    col_index = x // tile_size  # Integer division to get the column index
    row_index = y // tile_size  # Integer division to get the row index
    return col_index, row_index


def convert_indices_to_chess_notation(col_index, row_index, board_size):
    """
    Converts column and row indices to chess notation (e.g., 'e', 4).
    
    Parameters:
        col_index (int): Column index.
        row_index (int): Row index.
        board_size (int): Number of squares per row or column.
    
    Returns:
        (str, int): Position in chess notation.
    """
    col_letter = chr(ord('a') + col_index)     # 'a' to 'h' for columns
    row_number = board_size - row_index        # '8' to '1' for rows (top to bottom)
    return col_letter, row_number