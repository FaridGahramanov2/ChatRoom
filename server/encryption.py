# encryption.py
import rsa

class ServerEncryption:
    @staticmethod
    def load_public_key(key_data):
        return rsa.PublicKey.load_pkcs1(key_data)

    @staticmethod
    def verify_key(public_key):
        try:
            test_message = rsa.encrypt(b'test', public_key)
            return True
        except:
            return False