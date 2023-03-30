import socket
import threading

class Chat:

    def __init__(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def start(self, host='', port=8080):
        
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        self.sock.bind((ip_address, port))
        self.sock.listen(1)
        print(f"Server started on {ip_address}:{port}")
        conn, addr = self.sock.accept()
        print(f"Connected to {addr}")
        threading.Thread(target=self.send, args=(conn,)).start()
        threading.Thread(target=self.receive, args=(conn,)).start()


    def join(self, host, port=8080):
        
        self.sock.connect((host, port))
        print(f"Connected to {host}:{port}")
        threading.Thread(target=self.send, args=(self.sock,)).start()
        threading.Thread(target=self.receive, args=(self.sock,)).start()


    def send(self, conn):

        while True:
            message = input('')
            conn.sendall(message.encode())


    def receive(self, conn):

        while True:
            message = conn.recv(1024).decode()
            if not message:
                break
            print(message)


if __name__ == '__main__':

    chat = Chat()

    mode = input("Enter 's' to start a server, 'j' to join a server: ")
    if mode == 's':
        chat.start()

    elif mode == 'j':
        host = input("Enter server host: ")
        port = int(input("Enter server port: "))
        chat.join(host, port)

    else:
        print("Invalid mode")