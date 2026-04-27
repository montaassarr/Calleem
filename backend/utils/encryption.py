"""
Encryption utilities for secure API key storage
Uses AES-256-GCM for authenticated encryption
"""

import os
import base64
from typing import Dict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import logging

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

def _load_master_key() -> bytes:
    """Load and validate MASTER_KEY lazily so missing env var doesn't crash at import time."""
    hex_val = os.getenv("MASTER_KEY")
    if not hex_val:
        raise ValueError(
            "MASTER_KEY environment variable not set. "
            "Generate one with: python3 -c 'import secrets; print(secrets.token_hex(32))'"
        )
    try:
        key = bytes.fromhex(hex_val)
    except ValueError:
        raise ValueError("MASTER_KEY must be a valid hex string (64 hex characters = 32 bytes)")
    if len(key) != 32:
        raise ValueError("MASTER_KEY must be 32 bytes (64 hex characters)")
    return key


def encrypt_value(plaintext: str) -> str:
    """Encrypt a value using AES-256-GCM. Returns "iv:ciphertext" (base64)."""
    if not plaintext:
        raise ValueError("Cannot encrypt empty value")

    master_key = _load_master_key()
    iv = os.urandom(12)
    aesgcm = AESGCM(master_key)
    ciphertext = aesgcm.encrypt(iv, plaintext.encode('utf-8'), None)

    iv_b64 = base64.b64encode(iv).decode('utf-8')
    ciphertext_b64 = base64.b64encode(ciphertext).decode('utf-8')
    return f"{iv_b64}:{ciphertext_b64}"


def decrypt_value(encrypted: str) -> str:
    """Decrypt a value produced by encrypt_value."""
    if not encrypted or ':' not in encrypted:
        raise ValueError("Invalid encrypted value format")

    try:
        iv_b64, ciphertext_b64 = encrypted.split(':', 1)
        iv = base64.b64decode(iv_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        master_key = _load_master_key()
        aesgcm = AESGCM(master_key)
        plaintext_bytes = aesgcm.decrypt(iv, ciphertext, None)
        return plaintext_bytes.decode('utf-8')
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise ValueError("Failed to decrypt value - key may be corrupted or master key changed")


def mask_api_key(key: str, visible_chars: int = 4) -> str:
    """
    Mask an API key for display
    
    Args:
        key: The API key to mask
        visible_chars: Number of characters to show at the end
        
    Returns:
        Masked key like "sk-••••••••••••1234"
    """
    if not key:
        return ""
    
    if len(key) <= visible_chars:
        return "••••"
    
    # Detect prefix (e.g., "sk-", "xai-")
    prefix = ""
    if '-' in key[:10]:
        prefix = key.split('-')[0] + '-'
        key_without_prefix = key[len(prefix):]
    else:
        key_without_prefix = key
    
    # Show last N characters
    visible = key_without_prefix[-visible_chars:]
    masked_length = len(key_without_prefix) - visible_chars
    
    return f"{prefix}{'•' * min(masked_length, 20)}{visible}"
