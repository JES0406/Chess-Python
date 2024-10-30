from src.Pieces.Pieces import *

class PieceCreator:
    def __init__(self) -> None:
        self.pieces = {
            "pawn": Pawn,
            "king": King,
            "queen": Queen,
            "rook": Rook,
            "bishop": Bishop,
            "knight": Knight,
        }

    def create_piece(self, piece_type: str, color: str) -> Piece:
        return self.pieces[piece_type](color)