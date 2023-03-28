import time
import socket
import threading

print("\nWelcome to Chat Room\n")
print("Initialising....\n")
time.sleep(1)

s = socket.socket()
shost = socket.gethostname()
ip = socket.gethostbyname(shost)
print(shost, "(", ip, ")\n")
host = input(str("Enter server address: "))
name = input(str("\nEnter your name: "))
port = 1234
print("\nTrying to connect to ", host, "(", port, ")\n")
time.sleep(1)
s.connect((host, port))
print("Connected...\n")

s.send(name.encode())
s_name = s.recv(1024)
s_name = s_name.decode()
print(s_name, "has joined the chat room\nEnter [e] to exit chat room\n")

def receive():
    while True:
        try:
            message = s.recv(1024)
            if not message:
                break
            message = message.decode()
            print(s_name, ":", message)
        except:
            break

def send():
    while True:
        try:
            message = input()
            if message == "[e]":
                message = "Left chat room!"
                s.send(message.encode())
                print("\n")
                break
            s.send(message.encode())
        except:
            break

# create the two threads
receive_thread = threading.Thread(target=receive)
send_thread = threading.Thread(target=send)

# start the threads
receive_thread.start()
send_thread.start()

# wait for the threads to finish
receive_thread.join()
send_thread.join()




