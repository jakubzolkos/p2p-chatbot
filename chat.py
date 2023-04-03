import socket
import threading


class Chat:

    def __init__(self):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_server = False
        self.connections = []


    def start(self, host='', port=2080):

        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        self.sock.bind((host, port))
        self.is_server = True
        self.sock.listen(5)
        print(f"Server started on {host}:{port}")

        while True:
            conn, addr = self.sock.accept()
            print(f"Connected to {addr}")
            self.connections.append(conn)
            threading.Thread(target=self.send, args=(conn,)).start()
            threading.Thread(target=self.receive, args=(conn, conn)).start()


    def join(self, host, port=2080):

        self.sock.connect((host, port))
        print(f"Connected to {host}:{port}")
        threading.Thread(target=self.send, args=(self.sock,)).start()
        threading.Thread(target=self.receive, args=(self.sock, self.sock)).start()


    def send(self, conn):

        while True:
            message = input('')

            if self.is_server:
                for connection in self.connections:
                    connection.sendall(message.encode())
            else:
                conn.sendall(message.encode())


    def receive(self, conn, sender_conn):

        while True:
            message = conn.recv(1024).decode()
            if not message:
                break

            print(message)
            if self.is_server:
                for connection in self.connections:
                    if connection != sender_conn:
                        connection.sendall(message.encode())


if __name__ == '__main__':

    chat = Chat()

    mode = input("Enter 's' to start a server, 'j' to join a server: ")
    if mode == 's':
        chat.start(host='127.0.1.1', port=2080)

    elif mode == 'j':
        # host = input("Enter server host: ")
        # port = int(input("Enter server port: "))
        chat.join("127.0.1.1", 2080)


    else:
        print("Invalid mode")
