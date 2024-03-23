import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import os

class Crpt: 
    def __init__(self, key) -> None:
        self.cipher = Fernet(key)

    def hash_data(self, data):
        sha256 = hashlib.sha256()
        sha256.update(data.encode())
        return sha256.hexdigest()

    def verify_hash(self, new_data, original_data):
        return self.hash_data(new_data) == original_data  

    def encrypt_password(self, password):
        """ 
        Takes pasword and returns encrypted bytes
        """

        return self.cipher.encrypt(password.encode())
    
    def decrypt_password(self, encrypted_password):
        """ 
        Takes encrypted password and returns string
        """

        return self.cipher.decrypt(encrypted_password).decode()

class SaltManager(object):
    def __init__(self, generate, path='.salt'):
        self.generate = generate
        self.path = path

    def get(self):
        if self.generate:
            return self._generate_and_store()
        return self._read()

    def _generate_and_store(self):
        salt = os.urandom(16)
        with open(self.path, 'wb') as f:
            f.write(salt)
        return salt

    def _read(self):
        with open(self.path, 'rb') as f:
            return f.read()
        
def derive_key(passphrase, generate_salt=False):
    salt = SaltManager(generate_salt)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt.get(),
        iterations=1000,
        backend=default_backend()
    )

    return base64.urlsafe_b64encode(kdf.derive(passphrase))