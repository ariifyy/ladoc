from cryptography.fernet import Fernet
import os

def get_fernet():
    # Get absolute path of the current file (crypto_utils.py)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(base_dir, "secret.key")

    if not os.path.exists(key_path):
        key = Fernet.generate_key()
        with open(key_path, "wb") as f:
            f.write(key)
    else:
        with open(key_path, "rb") as f:
            key = f.read()
    return Fernet(key)
