"""
Encryption utilities for API keys
Uses Fernet (symmetric encryption) for secure storage
"""

from cryptography.fernet import Fernet
from utils.config import settings
import base64
import logging

logger = logging.getLogger(__name__)

# Generate cipher from secret key
def get_cipher():
    """Get Fernet cipher from settings"""
    # Ensure the key is properly formatted for Fernet (32 url-safe base64-encoded bytes)
    key = settings.SECRET_KEY.encode()
    # Fernet requires a 32-byte key, so we'll use the first 32 bytes of the hash
    from hashlib import sha256
    hashed_key = sha256(key).digest()
    encoded_key = base64.urlsafe_b64encode(hashed_key)
    return Fernet(encoded_key)


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage"""
    try:
        cipher = get_cipher()
        encrypted = cipher.encrypt(api_key.encode())
        return encrypted.decode()
    except Exception as e:
        logger.error(f"Error encrypting API key: {e}")
        raise


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key for use"""
    try:
        cipher = get_cipher()
        decrypted = cipher.decrypt(encrypted_key.encode())
        return decrypted.decode()
    except Exception as e:
        logger.error(f"Error decrypting API key: {e}")
        raise
