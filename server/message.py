# message.py
class MessageHandler:
    def __init__(self):
        self.message_queue = []

    def broadcast(self, message, sender, recipients):
        for client in recipients:
            if client != sender:
                client.send(message)

    def private_message(self, message, sender, recipient):
        recipient.send('MESSAGE'.encode('ascii'))
        recipient.send(message)