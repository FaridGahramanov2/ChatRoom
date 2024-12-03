# server/server.py
import socket
import threading
from encryption import ServerEncryption

class ChatServer:
    def __init__(self, host='127.0.0.1', port=55557):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = []
        self.nicknames = []
        self.encryption = ServerEncryption()
        self.keys = {}

    def broadcast(self, message, sender=None):
        print(f"Broadcasting: {message}")
        try:
            for client in self.clients:
                if client != sender:
                 client.send(message)
        except:
            pass

    def handle_client(self, client):
        try:
            client.send('KEY'.encode('ascii'))
            key_data = client.recv(1024)
            self.keys[client] = self.encryption.load_public_key(key_data)
        
            while True:
                message = client.recv(1024)
                if message:
                    self.broadcast(message)
        except:
            if client in self.clients:
                self.remove_client(client)

    def remove_client(self, client):
        if client in self.clients:
            index = self.clients.index(client)
            self.clients.remove(client)
            nickname = self.nicknames[index]
            self.nicknames.remove(nickname)
            self.broadcast(f"{nickname} left!".encode('ascii'))

    def start(self):
        print("Server running...")
        while True:
            client, address = self.server.accept()
            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            self.nicknames.append(nickname)
            self.clients.append(client)
            print(f"Connected: {nickname}")
            self.broadcast(f"{nickname} joined!".encode('ascii'))
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

if __name__ == "__main__":
    server = ChatServer()
    server.start()