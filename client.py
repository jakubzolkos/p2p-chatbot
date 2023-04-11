from socket import AF_INET, SOCK_STREAM
import socket
from threading import Thread
import tkinter

def servertest():

    hostpattern = '127.0.0'
    hostrange = 255
    port = 33001

    for i in range(hostrange):
        args = socket.getaddrinfo(hostpattern + '.' + str(i), port, socket.AF_INET, socket.SOCK_STREAM)
        for family, socktype, proto, canonname, sockaddr in args:
            s = socket.socket(family, socktype, proto)
            try:
                s.connect(sockaddr)
                print(sockaddr)
            except socket.error:
                pass
            else:
                s.close()


class Server:
    
    def __init__(self, host='', port=33000, buf_size=1024):

        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.server = socket.socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.clients = {}
        self.addresses = {}
    

    def start(self):

        self.server.listen(5)
        print("Waiting for connection...")
        while True:
            client, client_address = self.server.accept()
            print("%s:%s has connected." % client_address)
            client.send(bytes("Enter your name:", "utf8"))
            self.addresses[client] = client_address
            Thread(target=self.handle_client, args=(client,)).start()


    def handle_client(self, client):

        name = client.recv(self.buf_size).decode("utf8")
        welcome = f"Hello {name}! Enter {{quit}} to exit."
        client.send(bytes(welcome, "utf8"))
        msg = "%s has joined the chat!" % name
        self.broadcast(bytes(msg, "utf8"))
        self.clients[client] = name

        while True:
            msg = client.recv(self.buf_size)
            if msg != bytes("{quit}", "utf8"):
                self.broadcast(msg, name+": ")
            else:
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del self.clients[client]
                self.broadcast(bytes("%s has left the chat." % name, "utf8"))
                break


    def broadcast(self, msg, prefix=""):

        for sock in self.clients:
            sock.send(bytes(prefix, "utf8")+msg)


    def stop(self):

        self.server.close()


    def listen_for_test(self):
        
        test_server = socket.socket(AF_INET, SOCK_STREAM)
        test_server.bind((self.host, self.port + 1))
        test_server.listen(1)

        while True:
            client, client_address = test_server.accept()
            client.close()

    def start_server_thread(self):
        self.server_thread = Thread(target=self.listen_for_test)
        self.server_thread.start()


class ChatClient:

    def __init__(self, host, port):

        self.HOST = host
        self.PORT = port
        self.BUFSIZ = 1024
        self.ADDR = (self.HOST, self.PORT)

        self.client_socket = socket.socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(self.ADDR)

        self.top = tkinter.Tk()
        self.top.title("Chatter")

        self.messages_frame = tkinter.Frame(self.top)
        self.my_msg = tkinter.StringVar()
        self.scrollbar = tkinter.Scrollbar(self.messages_frame)

        self.msg_list = tkinter.Listbox(self.messages_frame, height=15, width=50, yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
        self.msg_list.pack()
        self.messages_frame.pack()

        self.entry_field = tkinter.Entry(self.top, textvariable=self.my_msg)
        self.entry_field.bind("<Return>", self.send)
        self.entry_field.pack()
        self.send_button = tkinter.Button(self.top, text="Send", command=self.send)
        self.send_button.pack()

        self.top.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.receive_thread = Thread(target=self.receive)
        self.receive_thread.start()

        tkinter.mainloop()


    def receive(self):

        while True:
            try:
                msg = self.client_socket.recv(self.BUFSIZ).decode("utf8")
                self.msg_list.insert(tkinter.END, msg)

            except OSError:
                break


    def send(self, event=None):

        msg = self.my_msg.get()
        self.my_msg.set("") 
        self.client_socket.send(bytes(msg, "utf8"))
        if msg == "{quit}":
            self.client_socket.close()
            self.top.quit()


    def on_closing(self, event=None):

        self.my_msg.set("{quit}")
        self.send()


if __name__ == "__main__":

    mode = input("Press 's' to start a new server or 'j' to join an existing server: ")
    if mode == 's':
        server = Server('127.0.0.2')
        server.start_server_thread()
        server.start()

    elif mode == 'j':
        servertest()
        host = input("Enter hostname: ")
        port = int(input("Enter port: "))
        chat_client = ChatClient(host, port)


