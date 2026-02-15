"""
Event Ticket model - NFT tickets as Algorand ASAs
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from backend.database import Base


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    event_name = Column(String(200), nullable=False)
    owner_phone = Column(String(20), nullable=False)
    owner_address = Column(String(58), nullable=False)
    asset_id = Column(Integer, unique=True, nullable=False)  # Algorand ASA ID
    tx_id = Column(String(100))  # Transaction ID for NFT creation
    ticket_number = Column(String(50), unique=True, nullable=False)
    is_valid = Column(Boolean, default=True)
    is_used = Column(Boolean, default=False)
    ticket_metadata = Column(String(1000))  # JSON metadata (renamed from 'metadata' to avoid SQLAlchemy conflict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    used_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Ticket {self.event_name} - {self.ticket_number}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "event_name": self.event_name,
            "owner_phone": self.owner_phone,
            "asset_id": self.asset_id,
            "tx_id": self.tx_id,
            "ticket_number": self.ticket_number,
            "is_valid": self.is_valid,
            "is_used": self.is_used,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

