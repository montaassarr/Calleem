from cryptography.fernet import Fernet
import base64
import os
from typing import Optional

class SecurityUtils:
    def __init__(self):
        # In production, this should be loaded from env and consistent
        # For now, we derive it from the existing SECRET_KEY or generate a fallback
        key = os.getenv("SECRET_KEY", "supersecretkeyshouldbechangedinprod")
        # Fernet requires a 32-byte url-safe base64-encoded key
        # We'll pad/truncate the secret to 32 bytes and encode it
        key_bytes = key.encode('utf-8')
        if len(key_bytes) < 32:
            key_bytes = key_bytes.ljust(32, b'=')
        else:
            key_bytes = key_bytes[:32]
            
        self.fernet = Fernet(base64.urlsafe_b64encode(key_bytes))

    def encrypt(self, data: str) -> str:
        if not data:
            return ""
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> Optional[str]:
        if not token:
            return None
        try:
            return self.fernet.decrypt(token.encode()).decode()
        except Exception:
            return None

security = SecurityUtils()
