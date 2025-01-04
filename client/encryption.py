# encryption.py
import rsa

class ClientEncryption:
    def __init__(self):
        self.public_key, self.private_key = rsa.newkeys(1024)
        self.partner_key = None

    def encrypt(self, message):
        if not self.partner_key:
            return message.encode('ascii')
        return rsa.encrypt(message.encode('ascii'), self.partner_key)

    def decrypt(self, message):
        if not isinstance(message, bytes):
            return message
        try:
            return rsa.decrypt(message, self.private_key).decode('ascii')
        except:
            return message.decode('ascii')

    # Client encryption.py
    def get_public_key(self):
        """Return the public key in PEM format."""
        return self.public_key.save_pkcs1(format='PEM')

    def set_partner_key(self, key_data):
        self.partner_key = rsa.PublicKey.load_pkcs1(key_data)