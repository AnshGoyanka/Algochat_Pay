"""
User model - Maps phone numbers to Algorand wallets
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from backend.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, index=True, nullable=False)
    wallet_address = Column(String(58), unique=True, index=True, nullable=False)
    encrypted_private_key = Column(String(500), nullable=False)  # AES encrypted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User {self.phone_number} - {self.wallet_address[:8]}...>"
    
    def to_dict(self):
        """Safe dictionary representation (excludes private key)"""
        return {
            "id": self.id,
            "phone_number": self.phone_number,
            "wallet_address": self.wallet_address,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
