# connection.py
class ConnectionManager:
    def __init__(self):
        self.connections = {}

    def add_connection(self, client, nickname, public_key=None):
        self.connections[client] = {
            'nickname': nickname,
            'public_key': public_key
        }

    def remove_connection(self, client):
        if client in self.connections:
            del self.connections[client]