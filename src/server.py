import socket
import time

# Configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 12345      # Port to bind to for server

# Setup server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print("Waiting for a connection...")

conn, addr = server_socket.accept()
print(f"Connected by {addr}")

def send_move(move, retries=3, timeout=1):
    for attempt in range(retries):
        try:
            conn.sendall(move.encode())
            conn.settimeout(timeout)
            ack = conn.recv(1024).decode()
            if ack == 'ACK':
                print("Move confirmed by opponent.")
                return True
        except socket.timeout:
            print(f"Timeout, retrying ({attempt + 1}/{retries})...")
    print("Move not confirmed. Connection issue.")
    return False

def receive_move():
    move = conn.recv(1024).decode()
    conn.sendall("ACK".encode())  # Send confirmation
    return move

try:
    while True:
        # Your game logic to decide on a move
        move = input("Enter your move in algebraic notation (e.g., e2e4): ")
        
        if send_move(move):
            # Update your game state here
            print(f"Sent move: {move}")
        
        print("Waiting for opponent's move...")
        opponent_move = receive_move()
        print(f"Received opponent's move: {opponent_move}")
        # Update your game state with opponent's move here

finally:
    conn.close()
    server_socket.close()
