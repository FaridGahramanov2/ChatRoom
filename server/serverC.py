import socket
import threading
from encryption import ServerEncryption
from server.connection import ConnectionManager
from server.utils import Utils


class ChatServer:
    def __init__(self, host='127.0.0.1', port=55557):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen()
        self.connections = ConnectionManager()
        self.encryption = ServerEncryption()

    def broadcast(self, message, sender=None):
        """Broadcast a message to all clients except the sender."""
        for client in self.connections.get_all_clients_except(sender):
            try:
                client.send(message)
            except:
                self.remove_client(client)

    def handle_client(self, client):
        try:
            # Step 1: Exchange Public Key
            client.send('KEY'.encode('ascii'))  # Request the client's public key
            key_data = client.recv(2048)  # Use larger buffer size for PEM keys
            public_key = self.encryption.load_public_key(key_data)  # Decode and load the key

            # Step 2: Exchange Nickname
            client.send('NICK'.encode('ascii'))  # Request the client's nickname
            nickname = client.recv(1024).decode('ascii')

            # Step 3: Store Client Information
            client_address = client.getpeername()  # Get the client's public IP and port
            self.connections.add_connection(client, nickname, client_address, public_key)

            # Notify Other Clients
            print(f"Connected: {nickname} ({client_address})")
            self.broadcast(f"{nickname} joined!".encode('ascii'))

            # Step 4: Communication Loop
            while True:
                message = client.recv(1024).decode('ascii')

                if message.startswith('DISCOVER'):
                    # Handle Peer Discovery
                    _, target_nickname = message.split(':', 1)
                    target_client, details = self.connections.get_client_by_nickname(target_nickname)
                    if target_client:
                        peer_info = f"PEER_INFO:{details['address'][0]}:{details['address'][1]}"
                        client.send(peer_info.encode('ascii'))
                    else:
                        client.send(f"ERROR: User {target_nickname} not found.".encode('ascii'))
                else:
                    # Broadcast Messages to All Clients
                    self.broadcast(message.encode('ascii'), sender=client)

        except Exception as e:
            # Handle Errors and Disconnect Client
            Utils.handle_error(e, client)
            self.remove_client(client)

    def remove_client(self, client):
        """Remove a client and notify others."""
        if client in self.connections.connections:
            nickname = self.connections.connections[client]['nickname']
            self.connections.remove_connection(client)
            self.broadcast(f"{nickname} left!".encode('ascii'))

    # def start(self):
    #     """Start the server and accept client connections."""
    #     print("Server running...")
    #     while True:
    #         client, address = self.server.accept()
    #         print(f"New connection from {address}")
    #         thread = threading.Thread(target=self.handle_client, args=(client,))
    #         thread.start()

    def start(self):
        print("Server running...")
        udp_thread = threading.Thread(target=self.handle_udp_discovery)
        udp_thread.start()

        while True:
            client, address = self.server.accept()
            thread = threading.Thread(target=self.handle_client, args=(client,))
            thread.start()

    # server/serverC.py

    def handle_udp_discovery(self):
        """Handle initial UDP hole punching."""
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket.bind(('0.0.0.0', 55558))  # Choose a port for UDP signaling

        print("UDP hole punching server running...")
        while True:
            data, addr = udp_socket.recvfrom(1024)
            print(f"Received UDP packet from {addr}: {data.decode('ascii')}")

            # Handle UDP discovery (optional relay or acknowledgment)
            target_nickname = data.decode('ascii')
            target_client, details = self.connections.get_client_by_nickname(target_nickname)
            if target_client:
                peer_info = f"{details['address'][0]}:{details['address'][1]}"
                udp_socket.sendto(peer_info.encode('ascii'), addr)
            else:
                udp_socket.sendto("ERROR: User not found.".encode('ascii'), addr)


if __name__ == "__main__":
    server = ChatServer()
    server.start()