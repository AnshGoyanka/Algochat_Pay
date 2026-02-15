"""
Merchant model - For privacy-enhanced payments
Allows hiding wallet addresses and showing friendly merchant names
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from backend.database import Base


class MerchantType(str, enum.Enum):
    EVENT_ORGANIZER = "event_organizer"
    FUNDRAISER = "fundraiser"
    BUSINESS = "business"
    INDIVIDUAL = "individual"


class Merchant(Base):
    __tablename__ = "merchants"
    
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(String(20), unique=True, nullable=False, index=True)  # "M12345"
    merchant_name = Column(String(200), nullable=False)  # Display name
    merchant_type = Column(SQLEnum(MerchantType), default=MerchantType.BUSINESS)
    phone_number = Column(String(20), index=True)  # Optional: links to users table
    wallet_address = Column(String(58), nullable=False)  # Algorand address
    description = Column(String(500))  # Business description
    is_active = Column(Boolean, default=True)
    
    # Link to events or funds
    event_id = Column(Integer)  # Link to events table
    fund_id = Column(Integer)   # Link to funds table
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Merchant {self.merchant_id} - {self.merchant_name}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "merchant_id": self.merchant_id,
            "merchant_name": self.merchant_name,
            "merchant_type": self.merchant_type.value,
            "description": self.description,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
