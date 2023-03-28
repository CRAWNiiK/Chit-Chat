import socket
import threading
import os

# set up the client
HOST = 'localhost'
PORT = 5555

nickname = input("Enter your nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

# function to handle incoming messages
def receive():
    while True:
        try:
            msg = client.recv(1024).decode()
            if msg:
                print(msg)
        except:
            print("An error occurred!")
            client.close()
            break

# function to handle file uploads
def upload(filename):
    try:
        with open(filename, 'rb') as f:
            client.send(f"{nickname} uploaded {filename}".encode())
            while True:
                data = f.read(1024)
                if not data:
                    break
                client.sendall(data)
            print("File upload complete!")
    except:
        print("Error uploading file")

# function to handle file downloads
def download(filename):
    try:
        client.send(f"/download {filename}".encode())
        data = client.recv(1024).decode()
        if data.startswith('File not found'):
            print(data)
        else:
            with open(filename, 'wb') as f:
                while True:
                    data = client.recv(1024)
                    if not data:
                        break
                    f.write(data)
                print(f"File {filename} download complete!")
    except:
        print("Error downloading file")

# function to list files in the upload directory
def list_files():
    try:
        client.send("/list-files".encode())
        data = client.recv(1024).decode()
        if data.startswith('Error'):
            print(data)
        else:
            files = data.split(',')
            for file in files:
                print(file)
    except:
        print("Error listing files")

# start the receive thread
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# loop to handle user input
while True:
    msg = input()

    if msg == '/quit':
        client.send('quit'.encode())
        client.close()
        break

    elif msg.startswith('/upload'):
        parts = msg.split(' ')
        if len(parts) < 2:
            print('Invalid command. Usage: /upload <filename>')
        else:
            filename = parts[1]
            if not os.path.isfile(filename):
                print('File does not exist')
            else:
                upload(filename)

    elif msg.startswith('/download'):
        parts = msg.split(' ')
        if len(parts) < 2:
            print('Invalid command. Usage: /download <filename>')
        else:
            filename = parts[1]
            download(filename)

    elif msg == '/list-files':
        list_files()

    else:
        client.send(f"{nickname}: {msg}".encode())