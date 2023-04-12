from socket import AF_INET, SOCK_STREAM
import socket
from threading import Thread
import tkinter
import sqlite3
import pandas as pd
import os
import random
import time
from collections import OrderedDict
from itertools import islice


# -------------------------- HELPERS --------------------------

def generate_chatroom(running_chatrooms, name):

    # Define the range of IP addresses to try
    ip_range = range(1, 101)

    # Define the range of ports to try
    port_range = range(50001, 50101)

    # Shuffle the IP addresses and ports to randomize the search order
    ip_addresses = list(ip_range)
    random.shuffle(ip_addresses)
    ports = list(port_range)
    random.shuffle(ports)

    # Try each combination of IP address and port until an unused one is found
    for ip in ip_addresses:
        host = f"127.0.0.{ip}"
        for port in ports:
            if not any(v == [host, port] for v in running_chatrooms.values()):
                # Found an unused host and port combination
                running_chatrooms[name] = [host, port]
                return running_chatrooms, host, port

    # If we get here, we didn't find an unused host and port combination
    raise Exception("Could not generate new chatroom address: all addresses in use.")


def display_chatrooms(chatrooms):

    # Get the length of the longest chatroom name for formatting purposes
    max_len = max(len(name) for name in chatrooms.keys())
    
    # Display the chatrooms in a formatted table
    print('\n')
    print("#".ljust(2), "|", "CHATROOM".ljust(max_len))
    print("-" * (max_len + 6))

    for i, (name, (_, _)) in enumerate(chatrooms.items(), start=1):
        print(str(i).ljust(2), "|", name.ljust(max_len))

    print('\n')

def search_chatrooms():

    chatrooms = OrderedDict()

    index = 1
    for i in range(1, 100):
        for port in range(1, 100):
            args = socket.getaddrinfo('127.0.0.' + str(i), port + 51000, socket.AF_INET, socket.SOCK_STREAM)
            for family, socktype, proto, canonname, sockaddr in args:
                s = socket.socket(family, socktype, proto)
                try:
                    s.connect(sockaddr)
                    chatroom_name = s.recv(1024).decode('utf-8') 
                    chatrooms[chatroom_name] = [sockaddr[0], port]
                    index += 1
                except socket.error:
                    pass
                else:
                    s.close()

    return chatrooms


# -------------------------- CLASSES --------------------------


class Chatroom:
    
    def __init__(self, name, host='', port=2000, buf_size=1024):

        self.name = name
        self.host = host
        self.port = port
        self.buf_size = buf_size
        self.server = socket.socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.clients = {}
        self.addresses = {}
        self.messages = pd.DataFrame(columns=['sender', 'receiver', 'message', 'timestamp'])
    

    def start(self):

        self.server.listen(5)
        print("\nChatroom created !")
        while True:
            client, client_address = self.server.accept()
            print("%s:%s has connected." % client_address)
            client.send(bytes("Enter your name:", "utf8"))
            self.addresses[client] = client_address
            Thread(target=self.handle_client, args=(client,)).start()


    def handle_client(self, client):

        name = client.recv(self.buf_size).decode("utf8")
        welcome = f"Hello {name}! Enter [e] to exit."
        client.send(bytes(welcome, "utf8"))
        msg = "%s has joined the chat!" % name
        self.broadcast(bytes(msg, "utf8"))
        self.clients[client] = name

        while True:
            msg = client.recv(self.buf_size)
            if msg != bytes("[e]", "utf8"):
                message = msg.decode('utf-8')
                receivers = [client_name for client, client_name in self.clients.items() if client_name != name]
                self.messages = self.messages.append({'sender': name, 'receiver': ', '.join(receivers), 'message': message, 'timestamp': pd.Timestamp.now(), 'chatroom': self.name}, ignore_index=True)
                self.messages.to_sql('messages', sqlite3.connect('messages.db'), if_exists='append', index=False)
                self.broadcast(msg, name+": ")
            else:
                client.send(bytes("[e]", "utf8"))
                client.close()
                del self.clients[client]
                self.broadcast(bytes("%s has left the chat." % name, "utf8"))
                os._exit(0)


    def broadcast(self, msg, prefix=""):

        for sock in self.clients:
            sock.send(bytes(prefix, "utf8")+msg)


    def stop(self):

        self.server.close()


    def confirm_running(self):
        
        test_server = socket.socket(AF_INET, SOCK_STREAM)
        test_server.bind((self.host, self.port + 1000))
        test_server.listen(1)

        while True:
            client, _ = test_server.accept()
            client.send(bytes(self.name, "utf8"))
            client.close()
            
            
    def confirm_running_thread(self):
        self.server_thread = Thread(target=self.confirm_running)
        self.server_thread.start()


class Client:

    def __init__(self, name, host, port):

        self.NAME = name
        self.HOST = host
        self.PORT = port
        self.BUFSIZ = 1024
        self.ADDR = (self.HOST, self.PORT)

        self.client_socket = socket.socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(self.ADDR)

        self.top = tkinter.Tk()
        self.top.title(f"{self.NAME}")
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
        if msg == "[e]":
            self.client_socket.close()
            self.top.quit()
            os._exit(0)


    def on_closing(self, event=None):

        self.my_msg.set("[e]")
        self.send()


if __name__ == "__main__":

    print(f"\n{'-' * 33} CHATBOT {'-' * 33}\n")

    while True:

        # Select mode
        mode = input("Create (s) new chatroom or join (j) an existing chatroom?: ")
        # Return a list of currently available chatrooms: [ID, HOST, PORT, NAME]
        running_chatrooms = search_chatrooms()
        
        if mode == 's':

            try:
                NAME = input("\nChatroom name: ")
                running_chatrooms, HOST, PORT = generate_chatroom(running_chatrooms, NAME)
                server = Chatroom(NAME, HOST, PORT)
                server.confirm_running_thread()
                Thread(target = server.start, daemon=True).start()
                chat_client = Client(NAME, HOST, PORT)
            
            except:
                print("\nError when creating a chatroom.\n")

        elif mode == 'j':

            try:
                display_chatrooms(running_chatrooms)
                chatroom_id = int(input("Select a chatroom ID: "))
                chatroom = list(running_chatrooms.items())[chatroom_id-1]
                NAME, HOST, PORT = chatroom[0], chatroom[1][0], chatroom[1][1] + 50000
                chat_client = Client(NAME, HOST, PORT)
            
            except Exception as e:
                print("\nInvalid ID or no chatrooms available.\n")


