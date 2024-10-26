from constants import numbers, letters

class Board:
    def __init__(self) -> None:
        self._board = [[None for i in range(len(numbers))]]