import socket

# Define host and port number
host = 'localhost'
port = 12345

# Create socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind socket to host and port
s.bind((host, port))

# Listen for incoming connections
s.listen()

# Wait for connection from client
client, addr = s.accept()
print(f'Connected to {addr}')

# Loop to receive and send messages
while True:
    # Receive message from client
    message = client.recv(1024).decode()

    # Check if message is not empty
    if message:
        print(f'Received: {message}')

        # Send message back to client
        client.send(f'You said: {message}'.encode())

# Close connection
client.close()
