from cryptography.fernet import Fernet
from django.conf import settings

# Store this securely! Generate once using Fernet.generate_key()
FERNET_KEY = settings.FERNET_SECRET_KEY
fernet = Fernet(FERNET_KEY)

def encrypt_session_id(session_id: int) -> str:
    return fernet.encrypt(str(session_id).encode()).decode()

def decrypt_session_id(encrypted_id: str) -> int:
    return int(fernet.decrypt(encrypted_id.encode()).decode())
