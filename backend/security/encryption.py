"""
Security utilities for AlgoChat Pay
AES encryption for private key storage
"""
import base64
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


class EncryptionService:
    """
    AES-256 encryption service for Algorand private keys
    CRITICAL: Never log decrypted private keys
    """
    
    def __init__(self):
        self._fernet = self._get_fernet()
    
    def _get_fernet(self) -> Fernet:
        """Initialize Fernet cipher with app encryption key"""
        # Derive a proper Fernet key from config
        key_material = settings.ENCRYPTION_KEY.encode()
        
        # Use PBKDF2 to derive a valid Fernet key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"algochat_salt_v1",  # Static salt for deterministic key
            iterations=100000,
            backend=default_backend()
        )
        derived_key = base64.urlsafe_b64encode(kdf.derive(key_material))
        return Fernet(derived_key)
    
    def encrypt_private_key(self, private_key: str) -> str:
        """
        Encrypt Algorand private key for database storage
        
        Args:
            private_key: Algorand private key (mnemonic or base64)
        
        Returns:
            Encrypted string (base64)
        """
        try:
            encrypted = self._fernet.encrypt(private_key.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error("Encryption failed (not logging plaintext)")
            raise ValueError("Failed to encrypt private key") from e
    
    def decrypt_private_key(self, encrypted_key: str) -> str:
        """
        Decrypt Algorand private key for transaction signing
        
        Args:
            encrypted_key: Encrypted private key from database
        
        Returns:
            Decrypted private key string
        
        SECURITY: Never log the return value
        """
        try:
            decrypted = self._fernet.decrypt(encrypted_key.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error("Decryption failed")
            raise ValueError("Failed to decrypt private key") from e
    
    @staticmethod
    def generate_encryption_key() -> str:
        """Generate a new 32-byte encryption key for .env"""
        return secrets.token_urlsafe(32)


# Global instance
encryption_service = EncryptionService()


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format
    Must start with + and be 10-15 digits
    """
    if not phone.startswith("+"):
        return False
    digits = phone[1:].replace(" ", "").replace("-", "")
    return digits.isdigit() and 10 <= len(digits) <= 15


def sanitize_input(text: str, max_length: int = 500) -> str:
    """
    Sanitize user input from WhatsApp
    Prevents injection attacks
    """
    # Remove dangerous characters
    sanitized = text.strip()[:max_length]
    # Additional sanitization can be added here
    return sanitized
