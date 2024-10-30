# Game.py
import pygame
import socket
from src.Board import Board
from src.constants import tile_size, board_size, margin
from src.utils import get_tile_from_click, display
from src.click_logic import get_move
from src.moving_logic import evaluate_move

class Game:
    def __init__(self, is_server, host='127.0.0.1', port=12345):
        pygame.init()
        self.screen = pygame.display.set_mode((tile_size * board_size + 2 * margin, tile_size * board_size + 2 * margin))
        self.clock = pygame.time.Clock()
        self.board = Board()
        self.restore_values()
        self.is_server = is_server
        self.host = host
        self.port = port
        self.turn_white = True  # White starts the game
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if is_server:
            self.socket.bind((self.host, self.port))
            self.socket.listen(1)
            print("Waiting for a connection...")
            self.conn, _ = self.socket.accept()
            print("Client connected.")
        else:
            self.socket.connect((self.host, self.port))
            self.conn = self.socket
            print("Connected to server.")

    def send_move(self, move, retries=3, timeout=1):
        for attempt in range(retries):
            try:
                self.conn.sendall(move.encode())
                self.conn.settimeout(timeout)
                ack = self.conn.recv(1024).decode()
                if ack == 'ACK':
                    print("Move confirmed by opponent.")
                    return True
            except socket.timeout:
                print(f"Timeout, retrying ({attempt + 1}/{retries})...")
        print("Move not confirmed. Connection issue.")
        return False

    def socket_logic(self, position):
        if (self.turn_white and self.is_server) or (not self.turn_white and not self.is_server):
            # Current player's turn
            self.handle_click(position) 
            if self.move:
                if self.send_move(self.move):
                    print(f"Sent move: {self.move}")
                    self.turn_white = not self.turn_white
                    self.move = None
        else:
            # Opponent's turn
            print("Waiting for opponent's move...")
            opponent_move = self.receive_move()
            print(f"Received opponent's move: {opponent_move}")
            self.apply_move(opponent_move, self.is_server)  # Update board with opponent's move
            self.turn_white = not self.turn_white

    def apply_move(self, move, is_server):
        color = "w" if is_server else "b"
        move_success, message = evaluate_move(self.board, move, color)
        if move_success:
            self.check_victory_conditions(move)

    def receive_move(self):
        move = self.conn.recv(1024).decode()
        self.conn.sendall("ACK".encode())  # Send confirmation
        return move

    def restore_values(self):
        """
        Restores the game to its initial state.
        """
        self.board = Board()
        self.board.initialize_board()
        self.running = True
        self.turn = 0
        self.selected_tile = None
        self.victory = None

    def handle_events(self):
        """
        Processes all incoming events like quitting and clicking.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.socket_logic(event.pos)
            elif event.type == pygame.KEYDOWN:
                match event.key:
                    case pygame.K_r:
                        self.restore_values()
        if self.victory:
            print(f"Color {self.victory} has won")

    def handle_click(self, position):
        """
        Handles a click event at the given screen position.

        args:
        position (x, y): Position (x, y) that was clicked
        """
        tile = get_tile_from_click(position)
        if not tile:
            return  # Ignore clicks outside the board
        
        if not self.selected_tile:
            self.select_piece(tile)
        else:
            self.move_piece(tile)

    def select_piece(self, tile):
        """
        Selects a piece at the given tile if it belongs to the current player.
        """
        piece = self.board[tile]
        if piece and piece.color == self.get_turn_color():
            self.selected_tile = tile

    def move_piece(self, target_tile):
        """
        Attempts to move the selected piece to the target tile.
        If successful, toggles the turn and checks for end conditions.
        """
        if self.selected_tile:
            piece = self.board[self.selected_tile]
            move = get_move(self.board, self.selected_tile, target_tile, piece, piece.color)
            move_success, message = evaluate_move(self.board, move, piece.color)
            if move_success:
                self.move = move
                self.check_victory_conditions(move)
            self.selected_tile = None  # Deselect piece after move
        
    def get_turn_color(self):
        """
        Returns the color of the player whose turn it is.
        """
        return 'w' if self.turn == 0 else 'b'

    def check_victory_conditions(self, move):
        """
        Checks for end-of-game conditions such as checkmate or stalemate.
        """
        # Placeholder logic; implement checkmate/stalemate detection here
        if "#" in move:
            self.victory = self.get_turn_color()

    def render(self):
        """
        Renders the game screen and board.
        """
        self.screen.fill("grey")
        display(self.screen)
        self.board.draw(self.screen)
        pygame.display.flip()

    def mainloop(self):
        """
        Runs the main game loop.
        """
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.mainloop()
