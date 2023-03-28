import socket
import threading

class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        self.connections = []

    def handle_peer(self, conn, addr):
        while True:
            data = conn.recv(1024)
            if not data:
                break
            for c in self.connections:
                c.send(data)
        conn.close()

    def connect(self, host, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        self.connections.append(sock)
        t = threading.Thread(target=self.handle_peer, args=(sock, (host, port)))
        t.start()

    def start(self):
        while True:
            conn, addr = self.sock.accept()
            self.connections.append(conn)
            t = threading.Thread(target=self.handle_peer, args=(conn, addr))
            t.start()

if __name__ == '__main__':
    p1 = Peer('localhost', 8888)
    p2 = Peer('localhost', 8889)
    p1.connect('localhost', 8889)
    p2.connect('localhost', 8888)
    p1.connections[0].send('Hello from Peer 1'.encode())
    p2.connections[0].send('Hello from Peer 2'.encode())

