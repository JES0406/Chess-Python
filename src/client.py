import socket
import time

# Configuration
HOST = '127.0.0.1'  # Server's IP address
PORT = 12345        # Port to connect to

# Setup client
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
print("Connected to server.")

def send_move(move, retries=3, timeout=1):
    for attempt in range(retries):
        try:
            client_socket.sendall(move.encode())
            client_socket.settimeout(timeout)
            ack = client_socket.recv(1024).decode()
            if ack == 'ACK':
                print("Move confirmed by opponent.")
                return True
        except socket.timeout:
            print(f"Timeout, retrying ({attempt + 1}/{retries})...")
    print("Move not confirmed. Connection issue.")
    return False

def receive_move():
    move = client_socket.recv(1024).decode()
    client_socket.sendall("ACK".encode())  # Send confirmation
    return move

try:
    while True:
        print("Waiting for opponent's move...")
        opponent_move = receive_move()
        print(f"Received opponent's move: {opponent_move}")
        # Update your game state with opponent's move here

        # Your game logic to decide on a move
        move = input("Enter your move in algebraic notation (e.g., e2e4): ")

        if send_move(move):
            # Update your game state here
            print(f"Sent move: {move}")

finally:
    client_socket.close()
