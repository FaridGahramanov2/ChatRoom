# server.py
# Main server class handling client connections, message routing and encryption
# Supports both private and group chat modes with RSA encryption

import socket
import threading
import rsa

class ChatServer:
   def __init__(self, host='127.0.0.1', port=55555):
       self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       self.server.bind((host, port))
       self.server.listen()
       
       # Track connected clients
       self.clients = []
       self.nicknames = []
       self.keys = []
       self.partners = []
       self.group = []

   def start(self):
       print("Server running...")
       while True:
           client, address = self.server.accept()
           self._handle_new_connection(client, address)

   def _handle_new_connection(self, client, address):
       try:
           # Get username and chat mode choice
           client.send('NICK'.encode('ascii'))
           nickname = client.recv(1024).decode('ascii')
           client.send('CHOICE'.encode('ascii'))
           choice = client.recv(1024).decode('ascii')

           if choice == "2":  # Private chat
               self._setup_private_chat(client, nickname)
           else:  # Group chat
               self._setup_group_chat(client, nickname)

           # Start message handling thread
           thread = threading.Thread(target=self._handle_client, args=(client,))
           thread.start()

       except Exception as e:
           print(f"Error handling new connection: {e}")
           client.close()

   def _handle_client(self, client):
       while True:
           try:
               message = client.recv(1024)
               if not message:
                   break
               self._route_message(client, message)
           except:
               self._remove_client(client)
               break

if __name__ == "__main__":
   server = ChatServer()
   server.start()