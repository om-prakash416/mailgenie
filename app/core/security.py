from cryptography.fernet import Fernet
import os, json

FERNET_KEY = os.getenv("FERNET_KEY")
fernet = Fernet(FERNET_KEY)

def encrypt_data(data: dict) -> str:
    return fernet.encrypt(json.dumps(data).encode()).decode()

def decrypt_data(token: str) -> dict:
    return json.loads(fernet.decrypt(token.encode()).decode())
