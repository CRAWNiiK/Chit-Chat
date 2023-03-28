import socket
import threading
import os

HOST = 'localhost'
PORT = 5555

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(f"Server is running on {HOST}:{PORT}")

clients = []
nicknames = {}
uploads_dir = './uploads/'

def broadcast(message):
    for client in clients:
        client.send(message.encode())

def handle(client, nickname):
    while True:
        try:
            message = client.recv(1024).decode()
            if message.startswith('/'):
                if message.startswith('/upload'):
                    filename = message.split()[1]
                    if filename.split('.')[-1] in ['txt', 'pem', 'jpeg', 'png', 'mp3', 'mp4']:
                        client.send("OK".encode())
                        with open(os.path.join(uploads_dir, filename), 'wb') as f:
                            while True:
                                data = client.recv(1024)
                                if not data:
                                    break
                                f.write(data)
                            f.close()
                        broadcast(f"{nickname} has uploaded a file: {filename}")
                    else:
                        client.send("ERROR: Invalid file extension".encode())
                elif message.startswith('/download'):
                    filename = message.split()[1]
                    if os.path.isfile(os.path.join(uploads_dir, filename)):
                        client.send(f"OK {filename}".encode())
                        with open(os.path.join(uploads_dir, filename), 'rb') as f:
                            data = f.read(1024)
                            while data:
                                client.send(data)
                                data = f.read(1024)
                        f.close()
                    else:
                        client.send("ERROR: File does not exist".encode())
                elif message.startswith('/list-files'):
                    files = os.listdir(uploads_dir)
                    client.send(f"OK {','.join(files)}".encode())
            else:
                broadcast(f"{nickname}: {message}")
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[client]
            nicknames.pop(client)
            broadcast(f"{nickname} has left the chat!")
            break

while True:
    client, address = server.accept()
    client.send("NICK".encode())
    nickname = client.recv(1024).decode()
    nicknames[client] = nickname
    clients.append(client)
    print(f"Nickname of the client is {nickname}")
    broadcast(f"{nickname} has joined the chat!")
    threading.Thread(target=handle, args=(client, nickname)).start()