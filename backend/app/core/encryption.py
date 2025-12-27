"""
Field-Level Encryption Module

AES-256-GCM encryption for sensitive health data fields.
Provides encryption/decryption utilities for PII and PHI.
"""

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    AES-256-GCM encryption service for field-level encryption.
    
    Uses PBKDF2 key derivation from a master key for additional security.
    Each encryption operation uses a unique nonce for security.
    """
    
    def __init__(self):
        """Initialize encryption service with key derivation."""
        # Derive encryption key from master key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=b'jeevan_health_salt',  # In production, use a secure random salt
            iterations=100000,
            backend=default_backend()
        )
        
        # Use encryption key from settings or derive from secret key
        master_key = settings.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0')
        self.key = kdf.derive(master_key)
        self.aesgcm = AESGCM(self.key)
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string using AES-256-GCM.
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            Base64-encoded encrypted string with nonce prepended
        """
        if not plaintext:
            return ""
        
        try:
            # Generate random nonce (12 bytes for GCM)
            nonce = os.urandom(12)
            
            # Encrypt
            plaintext_bytes = plaintext.encode('utf-8')
            ciphertext = self.aesgcm.encrypt(nonce, plaintext_bytes, None)
            
            # Combine nonce + ciphertext and encode
            encrypted_data = nonce + ciphertext
            return base64.b64encode(encrypted_data).decode('utf-8')
        
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise ValueError(f"Failed to encrypt data: {e}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt an encrypted string.
        
        Args:
            encrypted_data: Base64-encoded encrypted string with nonce
            
        Returns:
            Decrypted plaintext string
        """
        if not encrypted_data:
            return ""
        
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            
            # Extract nonce (first 12 bytes) and ciphertext
            nonce = encrypted_bytes[:12]
            ciphertext = encrypted_bytes[12:]
            
            # Decrypt
            plaintext_bytes = self.aesgcm.decrypt(nonce, ciphertext, None)
            return plaintext_bytes.decode('utf-8')
        
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise ValueError(f"Failed to decrypt data: {e}")
    
    def encrypt_dict_field(self, data: dict, field_name: str) -> dict:
        """
        Encrypt a specific field in a dictionary.
        
        Args:
            data: Dictionary containing the field
            field_name: Name of the field to encrypt
            
        Returns:
            Dictionary with encrypted field
        """
        if field_name in data and data[field_name]:
            data[field_name] = self.encrypt(str(data[field_name]))
        return data
    
    def decrypt_dict_field(self, data: dict, field_name: str) -> dict:
        """
        Decrypt a specific field in a dictionary.
        
        Args:
            data: Dictionary containing the encrypted field
            field_name: Name of the field to decrypt
            
        Returns:
            Dictionary with decrypted field
        """
        if field_name in data and data[field_name]:
            try:
                data[field_name] = self.decrypt(str(data[field_name]))
            except ValueError:
                # If decryption fails, field might not be encrypted
                logger.warning(f"Failed to decrypt field {field_name}, leaving as-is")
        return data


# Global encryption service instance
encryption_service = EncryptionService()

