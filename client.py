import time
import socket
import threading
import sys

class ChatClient:

    def __init__(self):

        print("\nWelcome to Chat Room\n")
        print("Initialising....\n")
        time.sleep(1)

        self.s = socket.socket()
        self.shost = socket.gethostname()
        self.ip = socket.gethostbyname(self.shost)
        print(self.shost, "(", self.ip, ")\n")
        self.host = "127.0.1.1"
        self.name = input(str("\nEnter your name: "))
        self.port = 1234
        print("\nTrying to connect to ", self.host, "(", self.port, ")\n")
        time.sleep(1)
        self.s.connect((self.host, self.port))
        print("Connected...\n")

        self.s.send(self.name.encode())
        self.s_name = self.s.recv(1024)
        self.s_name = self.s_name.decode()
        print(self.s_name, "has joined the chat room\nEnter [e] to exit chat room\n")


    def receive(self):

        while True:
            try:
                message = self.s.recv(1024)
                if not message:
                    break
                message = message.decode()
                print(self.s_name, ":", message)

            except:
                break


    def send(self):
        with self.s:
            while True:
                try:
                    message = input()
                    if message == "[e]":
                        message = "Left chat room!"
                        self.s.send(message.encode())
                        print("\n")
                        sys.exit(0)

                    self.s.send(message.encode())

                except:
                    break


    def start_chat(self):

        # create the two threads
        receive_thread = threading.Thread(target=self.receive)
        send_thread = threading.Thread(target=self.send)

        # start the threads
        receive_thread.start()
        send_thread.start()

        # wait for the threads to finish
        receive_thread.join()
        send_thread.join()


if __name__ == '__main__':

    client = ChatClient()
    client.start_chat()
