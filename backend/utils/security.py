"""
Thin encrypt/decrypt wrapper — delegates to encryption.py (AES-256-GCM + MASTER_KEY).
The previous pad/truncate Fernet approach was removed because it was not a valid KDF.
"""

from utils.encryption import encrypt_value, decrypt_value
from typing import Optional


class SecurityUtils:
    def encrypt(self, data: str) -> str:
        if not data:
            return ""
        return encrypt_value(data)

    def decrypt(self, token: str) -> Optional[str]:
        if not token:
            return None
        try:
            return decrypt_value(token)
        except Exception:
            return None


security = SecurityUtils()
