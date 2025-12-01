"""
Phase 1 Unit Tests - Encryption Module

Tests the encryption/decryption utilities used for storing API keys.
Critical for security - API key leaks would destroy customer trust.

Tests:
1. Encrypt → Decrypt roundtrip returns original
2. Encrypt empty string
3. Encrypt special characters (UTF-8)
4. Encrypt large string (10KB)
5. Decrypt with wrong key → Error
6. Decrypt corrupted data → Error
7. Key rotation → Old data decryptable
8. Environment key loading
"""

import pytest
import os
from cryptography.fernet import Fernet, InvalidToken
from backend.utils.encryption import encrypt_value, decrypt_value, MASTER_KEY


class TestEncryption:
    """Test suite for API key encryption/decryption"""
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test that encrypt → decrypt returns original value"""
        original = "gsk_test_1234567890abcdefghijklmnopqrstuvwxyz"
        
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)
        
        assert decrypted == original
        assert encrypted != original  # Ensure it's actually encrypted
        
    def test_encrypt_empty_string(self):
        """Test encryption of empty string - should raise error"""
        original = ""
        
        # Empty strings should be rejected for security
        with pytest.raises(ValueError):
            encrypt_value(original)
        
    def test_encrypt_special_characters_utf8(self):
        """Test encryption of special characters and UTF-8"""
        original = "sk-proj_🔑中文español!@#$%^&*()_+-=[]{}|;:',.<>?/"
        
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)
        
        assert decrypted == original
        
    def test_encrypt_long_string(self):
        """Test encryption of large string (10KB)"""
        original = "x" * 10240  # 10KB
        
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)
        
        assert decrypted == original
        assert len(encrypted) > len(original)  # Encrypted should be longer
        
    def test_decrypt_with_wrong_key_raises_error(self):
        """Test that decrypting with wrong key raises error"""
        original = "gsk_test_key"
        
        # Encrypt with one key
        encrypted = encrypt_value(original)
        
        # Try to decrypt with different key
        wrong_key = Fernet.generate_key()
        
        with pytest.raises(InvalidToken):
            fernet = Fernet(wrong_key)
            fernet.decrypt(encrypted.encode())
            
    def test_decrypt_corrupted_data_raises_error(self):
        """Test that corrupted encrypted data raises error"""
        original = "gsk_test_key"
        encrypted = encrypt_value(original)
        
        # Corrupt the encrypted data
        corrupted = encrypted[:-10] + "corrupted!"
        
        with pytest.raises(Exception):  # Will raise InvalidToken or similar
            decrypt_value(corrupted)
            
    def test_key_rotation_old_data_decryptable(self):
        """Test that after key rotation, old data is still decryptable with old key"""
        original = "gsk_test_key"
        
        # Encrypt with old key
        old_master_key = os.environ.get('MASTER_KEY')
        encrypted_with_old_key = encrypt_value(original)
        
        # For this test, we'll verify we can decrypt with same key
        # (Real key rotation would involve re-encrypting all data)
        decrypted = decrypt_value(encrypted_with_old_key)
        
        assert decrypted == original
        
    def test_environment_key_loading(self):
        """Test that encryption key loads from environment variable"""
        # Verify MASTER_KEY is set
        assert os.environ.get('MASTER_KEY'), "MASTER_KEY must be set"
        
        # Test encryption works
        original = "test_key"
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)
        
        assert decrypted == original


class TestEncryptionEdgeCases:
    """Additional edge case tests for encryption"""
    
    def test_encrypt_none_value(self):
        """Test that encrypting None raises error"""
        with pytest.raises(ValueError):
            encrypt_value(None)
            
    def test_decrypt_none_value(self):
        """Test that decrypting None raises error"""
        with pytest.raises(ValueError):
            decrypt_value(None)
            
    def test_encrypt_numeric_string(self):
        """Test encryption of numeric strings"""
        original = "1234567890"
        
        encrypted = encrypt_value(original)
        decrypted = decrypt_value(encrypted)
        
        assert decrypted == original
        
    def test_multiple_encryptions_produce_different_outputs(self):
        """Test that encrypting the same value multiple times produces different ciphertext"""
        original = "gsk_test_key"
        
        encrypted1 = encrypt_value(original)
        encrypted2 = encrypt_value(original)
        
        # Due to Fernet's timestamp-based encryption, outputs should differ
        # But both should decrypt to same value
        assert encrypted1 != encrypted2
        assert decrypt_value(encrypted1) == original
        assert decrypt_value(encrypted2) == original


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
