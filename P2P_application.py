import socket
import threading

class Chatbot:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.users = ['10.239.208.17']
        self.sessions = {}

    def start_session(self, ip):
        self.sessions[ip] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sessions[ip].connect((ip, self.port))
        self.sessions[ip].send(f"Connected to {self.ip}".encode())

    def handle_client(self, client_socket, address):
        self.sessions[address[0]] = client_socket
        print(f"Connected to {address[0]}")
        while True:
            message = client_socket.recv(1024).decode()
            if message:
                print(f"{address[0]}: {message}")

    def listen(self):
        self.sock.bind((self.ip, self.port))
        self.sock.listen()
        while True:
            conn, addr = self.sock.accept()
            self.sessions[addr[0]] = conn
            threading.Thread(target=self.handle_client, args=(conn,)).start()

    def broadcast_message(self, message):
        for user in self.users:
            if user != self.ip: # Skip sending message to own IP address
                self.sessions[user].send(f"{self.ip}: {message}".encode())


if __name__ == "__main__":

    chatbot = Chatbot('10.239.208.17', 5000)

    for user in chatbot.users:
        if user != chatbot.ip:
            chatbot.start_session(user)

    threading.Thread(target=chatbot.listen).start()

    while True:
        message = input()
        chatbot.broadcast_message(message)