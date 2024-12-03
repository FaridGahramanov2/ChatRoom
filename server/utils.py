# utils.py
class Utils:
    @staticmethod
    def validate_nickname(nickname):
        return nickname.isalnum() and len(nickname) <= 32

    @staticmethod
    def format_message(message, sender):
        return f"{sender}: {message}"

    @staticmethod
    def handle_error(error, client=None):
        print(f"Error: {error}")
        if client:
            client.close()