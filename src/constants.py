import pygame


board_size = 8
tile_size = 128
theme = 'gray'


letters = [chr(i) for i in range(97, 97 + board_size)]
numbers = [i for i in range(1, board_size+1)]

path_of_piece = r"Visuals\{color}_{piece}_png_shadow_{size}px.png"
piece_size = '128'

path_of_bg = r"Visuals\square_{theme}_{color}_png_shadow_128px.png"

pygame.font.init()
font = pygame.font.SysFont(None, 36)

pieces = {
    'q': 'queen',
    'n': 'knight',
    'k': 'king',
    'b': 'bishop',
    'r': 'rook',
    'p': 'pawn'
}