import time
import socket
import threading

print("\nWelcome to Chat Room\n")
print("Initialising....\n")
time.sleep(1)

s = socket.socket()
host = socket.gethostname()
ip = socket.gethostbyname(host)
port = 1234
s.bind((host, port))
print(host, "(", ip, ")\n")
name = input(str("Enter your name: "))

s.listen(1)
print("\nWaiting for incoming connections...\n")
conn, addr = s.accept()
print("Received connection from ", addr[0], "(", addr[1], ")\n")

s_name = conn.recv(1024)
s_name = s_name.decode()
print(s_name, "has connected to the chat room\nEnter [e] to exit chat room\n")
conn.send(name.encode())

def listen():
    while True:
        try:
            message = conn.recv(1024)
            if not message:
                break
            message = message.decode()
            print(s_name, ":", message)
        except:
            break

def broadcast():
    while True:
        try:
            message = input()
            if message == "[e]":
                message = "Left chat room!"
                conn.send(message.encode())
                print("\n")
                break
            conn.send(message.encode())
        except:
            break

# create the two threads
listen_thread = threading.Thread(target=listen)
broadcast_thread = threading.Thread(target=broadcast)

# start the threads
listen_thread.start()
broadcast_thread.start()

# wait for the threads to finish
listen_thread.join()
broadcast_thread.join()