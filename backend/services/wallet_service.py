"""
Wallet service - User wallet management
Maps phone numbers to Algorand wallets (demo-safe)
"""
from sqlalchemy.orm import Session
from typing import Optional, Tuple
import logging
from backend.models.user import User
from backend.algorand.client import algorand_client
from backend.security.encryption import encryption_service, validate_phone_number
from backend.utils.demo_safety import safe_demo_operation
from backend.utils.production_logging import event_logger

logger = logging.getLogger(__name__)


class WalletService:
    """
    Manages user wallets
    Creates and retrieves Algorand wallets linked to phone numbers
    """
    
    @safe_demo_operation("create_wallet")
    def get_or_create_wallet(self, db: Session, phone_number: str) -> Tuple[User, bool]:
        """
        Get existing wallet or create new one for phone number (demo-safe with retry)
        
        Args:
            db: Database session
            phone_number: User's phone number (format: +1234567890)
        
        Returns:
            (User object, created_flag)
        """
        # Validate phone number
        if not validate_phone_number(phone_number):
            raise ValueError(f"Invalid phone number format: {phone_number}")
        
        # Check if user already exists
        user = db.query(User).filter(User.phone_number == phone_number).first()
        
        if user:
            logger.info(f"Retrieved existing wallet for {phone_number}")
            return user, False
        
        # Create new Algorand wallet
        private_key, address, mnemonic = algorand_client.create_wallet()
        
        # Encrypt private key before storage
        encrypted_key = encryption_service.encrypt_private_key(private_key)
        
        # Create user record
        user = User(
            phone_number=phone_number,
            wallet_address=address,
            encrypted_private_key=encrypted_key
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        # Log wallet creation event
        event_logger.wallet_created(phone_number, address)
        logger.info(f"Created new wallet for {phone_number}: {address}")
        return user, True
    
    def get_user_by_phone(self, db: Session, phone_number: str) -> Optional[User]:
        """Get user by phone number"""
        return db.query(User).filter(User.phone_number == phone_number).first()
    
    def get_user_by_address(self, db: Session, wallet_address: str) -> Optional[User]:
        """Get user by wallet address"""
        return db.query(User).filter(User.wallet_address == wallet_address).first()
    
    def get_private_key(self, db: Session, phone_number: str) -> str:
        """
        Get decrypted private key for transaction signing
        SECURITY: Never log the return value
        
        Args:
            db: Database session
            phone_number: User's phone number
        
        Returns:
            Decrypted private key
        
        Raises:
            ValueError: If user not found
        """
        user = self.get_user_by_phone(db, phone_number)
        
        if not user:
            raise ValueError(f"No wallet found for {phone_number}")
        
        # Decrypt and return private key
        return encryption_service.decrypt_private_key(user.encrypted_private_key)
    
    def get_balance(self, db: Session, phone_number: str) -> float:
        """
        Get wallet balance in ALGO
        
        Args:
            db: Database session
            phone_number: User's phone number
        
        Returns:
            Balance in ALGO
        """
        user = self.get_user_by_phone(db, phone_number)
        
        if not user:
            raise ValueError(f"No wallet found for {phone_number}")
        
        return algorand_client.get_balance(user.wallet_address)
    
    def get_wallet_info(self, db: Session, phone_number: str) -> dict:
        """
        Get comprehensive wallet information
        
        Returns:
            {
                "phone": str,
                "address": str,
                "balance": float,
                "created_at": str
            }
        """
        user = self.get_user_by_phone(db, phone_number)
        
        if not user:
            raise ValueError(f"No wallet found for {phone_number}")
        
        balance = algorand_client.get_balance(user.wallet_address)
        
        return {
            "phone": user.phone_number,
            "address": user.wallet_address,
            "balance": balance,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }


# Global service instance
wallet_service = WalletService()
