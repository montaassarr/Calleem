"""
Twilio Service - Phone Number Management
Handles Twilio phone number operations and SIP trunk integration
"""

import os
import logging
from typing import Optional, Dict, Any
from utils.encryption import encrypt_value, decrypt_value

logger = logging.getLogger(__name__)


class TwilioService:
    """
    Twilio integration service for phone number management.
    Handles phone number validation and credential encryption.
    """
    
    def __init__(self):
        """Initialize Twilio service"""
        logger.info("Twilio service initialized")
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format (E.164)
        
        Args:
            phone_number: Phone number to validate (should be +1234567890 format)
            
        Returns:
            True if valid, False otherwise
        """
        if not phone_number:
            return False
        
        # E.164 format: +[country code][number]
        # Should start with + and contain 10-15 digits
        if not phone_number.startswith('+'):
            return False
        
        # Remove + and check if remaining are digits
        digits = phone_number[1:]
        if not digits.isdigit():
            return False
        
        # Valid length (10-15 digits after +)
        if len(digits) < 10 or len(digits) > 15:
            return False
        
        return True
    
    def encrypt_credentials(
        self,
        account_sid: str,
        auth_token: str
    ) -> Dict[str, str]:
        """
        Encrypt Twilio credentials for secure storage
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token
            
        Returns:
            Dictionary with encrypted credentials
        """
        try:
            encrypted_sid = encrypt_value(account_sid)
            encrypted_token = encrypt_value(auth_token)
            
            return {
                "account_sid_encrypted": encrypted_sid,
                "auth_token_encrypted": encrypted_token
            }
        except Exception as e:
            logger.error(f"Failed to encrypt Twilio credentials: {e}")
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt_credentials(
        self,
        account_sid_encrypted: str,
        auth_token_encrypted: str
    ) -> Dict[str, str]:
        """
        Decrypt Twilio credentials for use
        
        Args:
            account_sid_encrypted: Encrypted Account SID
            auth_token_encrypted: Encrypted Auth Token
            
        Returns:
            Dictionary with decrypted credentials
        """
        try:
            account_sid = decrypt_value(account_sid_encrypted)
            auth_token = decrypt_value(auth_token_encrypted)
            
            return {
                "account_sid": account_sid,
                "auth_token": auth_token
            }
        except Exception as e:
            logger.error(f"Failed to decrypt Twilio credentials: {e}")
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number to E.164 standard
        
        Args:
            phone_number: Phone number (can be various formats)
            
        Returns:
            E.164 formatted phone number (+1234567890)
        """
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # If doesn't start with +, assume US number and add +1
        if not cleaned.startswith('+'):
            # If starts with 1 (country code), keep it
            if cleaned.startswith('1') and len(cleaned) == 11:
                cleaned = '+' + cleaned
            # Otherwise add +1 for US
            elif len(cleaned) == 10:
                cleaned = '+1' + cleaned
            else:
                cleaned = '+' + cleaned
        
        return cleaned


# Create global instance
twilio_service = TwilioService()
