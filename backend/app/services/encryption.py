from cryptography.fernet import Fernet, InvalidToken

from app.config import get_settings

settings = get_settings()
fernet = Fernet(settings.encryption_key.encode())


class DecryptionError(Exception):
    pass


def encrypt_api_key(raw_key: str) -> str:
    return fernet.encrypt(raw_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    try:
        return fernet.decrypt(encrypted_key.encode()).decode()
    except InvalidToken as exc:
        raise DecryptionError('Failed to decrypt API key') from exc
