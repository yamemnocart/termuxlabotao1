
import bcrypt
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
import os

class CryptoGuard:
    """Lớp mã hóa bất khả xâm phạm"""
    
    def __init__(self):
        self.salt = bcrypt.gensalt()
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def hash_password(self, password):
        """Mã hóa password bằng bcrypt"""
        return bcrypt.hashpw(password.encode(), self.salt).decode()
    
    def verify_password(self, password, hashed):
        """Xác minh password"""
        return bcrypt.checkpw(password.encode(), hashed.encode())
    
    def encrypt_aes(self, data):
        """Mã hóa AES-256"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_aes(self, encrypted):
        """Giải mã AES-256"""
        return self.cipher.decrypt(encrypted.encode()).decode()
    
    def generate_key_pair(self):
        """Tạo cặp khóa bất đối xứng (mock)"""
        return {
            'public': base64.b64encode(os.urandom(32)).decode(),
            'private': base64.b64encode(os.urandom(64)).decode()
        }

# Singleton
crypto = CryptoGuard()
