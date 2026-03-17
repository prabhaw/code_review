import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from app.config import settings


class EncryptDecrypt:
    kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=settings.ENCRYPTION_SALT,
    iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.ENCRYPTION_KEY))
    f = Fernet(key)

    def encrypt(self, data: str) -> str:
        return self.f.encrypt(data.encode()).decode()

    def decrypt(self, data: str) -> str:
        return self.f.decrypt(data.encode()).decode()