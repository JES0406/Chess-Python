board_size = 8
tile_size = 128
theme = 'brown'


letters = [chr(i) for i in range(61, 61 + board_size)]
numbers = [i for i in range(board_size + 1)]

path_of_piece = r"Visuals\{color}_{piece}_png_shadow_{size}px.png"
piece_size = '128'

path_of_bg = r"Visuals\square_{theme}_{color}_png_shadow_128px.png"