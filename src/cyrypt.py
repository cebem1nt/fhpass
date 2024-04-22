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

    def verify_hash(self, new_data, original_hash):
        return self.hash_data(new_data) == original_hash

    def encrypt_value(self, value):
        """ 
        Takes pasword and returns encrypted bytes
        """
        return self.cipher.encrypt(value.encode())
    
    def decrypt_value(self, encrypted_value):
        """ 
        Takes encrypted password and returns string
        """
        return self.cipher.decrypt(encrypted_value).decode()

class SaltManager(object):
    def __init__(self, generate):
        self.generate = generate
        self.HOME_DIR = os.path.expanduser('~')
        self.DIR = os.path.join(self.HOME_DIR, '.password_manager')

    def get(self):
        if self.generate:
            return self._generate_and_store()
        return self._read()

    def _generate_and_store(self):
        salt = os.urandom(16)

        if not os.path.exists(self.DIR):
            os.makedirs(self.DIR)

        with open(os.path.join(self.DIR, '.salt'), 'wb') as f:
            f.write(salt)

        return salt

    def _read(self):
        with open(os.path.join(self.DIR, '.salt'), 'rb') as f:
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