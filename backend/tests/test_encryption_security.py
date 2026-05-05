"""
Tests for utils/encryption.py (AES-256-GCM) and utils/security.py (SecurityUtils wrapper).

Verifies:
- encrypt/decrypt round-trip works correctly
- encrypt produces different ciphertext each call (random IV)
- decrypt rejects tampered ciphertext
- SecurityUtils.encrypt delegates to encryption.py (not legacy Fernet)
- SecurityUtils.decrypt returns None on bad input (no exception propagation)
- Empty input handling
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEncryptionRoundTrip:
    def test_encrypt_decrypt_plaintext(self):
        from utils.encryption import encrypt_value, decrypt_value
        plaintext = "super-secret-api-key-abc123"
        encrypted = encrypt_value(plaintext)
        assert decrypt_value(encrypted) == plaintext

    def test_encrypt_produces_iv_colon_format(self):
        from utils.encryption import encrypt_value
        result = encrypt_value("test-value")
        assert ":" in result, "Encrypted output must be 'iv:ciphertext'"
        parts = result.split(":", 1)
        assert len(parts) == 2
        assert len(parts[0]) > 0
        assert len(parts[1]) > 0

    def test_encrypt_is_nondeterministic(self):
        """Same plaintext must produce different ciphertext each call (random IV)."""
        from utils.encryption import encrypt_value
        plaintext = "same-input"
        c1 = encrypt_value(plaintext)
        c2 = encrypt_value(plaintext)
        assert c1 != c2, "AES-GCM must use a fresh random IV each encryption"

    def test_decrypt_rejects_tampered_ciphertext(self):
        from utils.encryption import encrypt_value, decrypt_value
        encrypted = encrypt_value("original")
        tampered = encrypted[:-4] + "XXXX"
        with pytest.raises(Exception):
            decrypt_value(tampered)

    def test_decrypt_rejects_missing_colon(self):
        from utils.encryption import decrypt_value
        with pytest.raises(ValueError):
            decrypt_value("nodivisioncharacterhere")

    def test_encrypt_rejects_empty_string(self):
        from utils.encryption import encrypt_value
        with pytest.raises(ValueError):
            encrypt_value("")

    def test_encrypt_long_value(self):
        from utils.encryption import encrypt_value, decrypt_value
        long_val = "x" * 10_000
        assert decrypt_value(encrypt_value(long_val)) == long_val


class TestMasterKeyValidation:
    def test_missing_master_key_raises(self, monkeypatch):
        monkeypatch.delenv("MASTER_KEY", raising=False)
        # _load_master_key reads os.getenv lazily on each call — no reload needed
        import utils.encryption as enc
        with pytest.raises(ValueError, match="MASTER_KEY"):
            enc.encrypt_value("test")

    def test_short_master_key_raises(self, monkeypatch):
        monkeypatch.setenv("MASTER_KEY", "deadbeef")  # only 4 bytes
        import importlib
        import utils.encryption as enc
        importlib.reload(enc)
        with pytest.raises(ValueError):
            enc.encrypt_value("test")

    def test_invalid_hex_master_key_raises(self, monkeypatch):
        monkeypatch.setenv("MASTER_KEY", "Z" * 64)  # not valid hex
        import importlib
        import utils.encryption as enc
        importlib.reload(enc)
        with pytest.raises(ValueError):
            enc.encrypt_value("test")


class TestSecurityUtils:
    def test_encrypt_returns_non_empty(self):
        from utils.security import SecurityUtils
        su = SecurityUtils()
        result = su.encrypt("hello")
        assert result != ""
        assert ":" in result

    def test_decrypt_roundtrip(self):
        from utils.security import SecurityUtils
        su = SecurityUtils()
        original = "my-secret-token"
        assert su.decrypt(su.encrypt(original)) == original

    def test_empty_string_returns_empty(self):
        from utils.security import SecurityUtils
        su = SecurityUtils()
        assert su.encrypt("") == ""
        assert su.decrypt("") is None

    def test_decrypt_bad_value_returns_none(self):
        """SecurityUtils.decrypt must swallow exceptions — callers expect None on failure."""
        from utils.security import SecurityUtils
        su = SecurityUtils()
        assert su.decrypt("garbage:data:xxxx") is None

    def test_does_not_import_fernet(self):
        """Security module must NOT import Fernet (legacy KDF was removed)."""
        import utils.security as sec_mod
        import inspect
        src = inspect.getsource(sec_mod)
        # Check for actual import statement, not just mention in comments/docstrings
        assert "import Fernet" not in src, "security.py must not import Fernet"
        assert "from cryptography.fernet" not in src, "security.py must not use Fernet"
        assert "ljust" not in src, "security.py must not use the old pad/truncate KDF"
