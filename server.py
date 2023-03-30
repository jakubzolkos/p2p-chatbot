import time
import socket
import threading

class ChatRoom:

    def __init__(self):

        print("\nWelcome to Chat Room\n")
        print("Initialising....\n")
        time.sleep(1)

        self.s = socket.socket()
        self.host = socket.gethostname()
        self.ip = socket.gethostbyname(self.host)
        self.port = 1234
        self.s.bind((self.host, self.port))
        print(self.host, "(", self.ip, ")\n")
        self.name = "Jakub"

        self.s.listen(1)
        print("\nWaiting for incoming connections...\n")
        self.conn, self.addr = self.s.accept()
        print("Received connection from ", self.addr[0], "(", self.addr[1], ")\n")

        self.s_name = self.conn.recv(1024)
        self.s_name = self.s_name.decode()
        print(self.s_name, "has connected to the chat room\nEnter [e] to exit chat room\n")
        self.conn.send(self.name.encode())


    def listen(self):

        while True:
            try:
                message = self.conn.recv(1024)
                if not message:
                    break
                message = message.decode()
                print(self.s_name, ":", message)

            except:
                break


    def broadcast(self):

        while True:
            try:
                message = input()
                if message == "[e]":
                    message = "Left chat room!"
                    self.conn.send(message.encode())
                    print("\n")
                    break
                self.conn.send(message.encode())

            except:
                break


    def run(self):

        listen_thread = threading.Thread(target=self.listen)
        broadcast_thread = threading.Thread(target=self.broadcast)

        listen_thread.start()
        broadcast_thread.start()

        listen_thread.join()
        broadcast_thread.join()


if __name__ == "__main__":

    chat_room = ChatRoom()
    chat_room.run()
