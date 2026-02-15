"""
Contact model - Maps nicknames to phone numbers for easy payments
Allows users to say "pay ansh 50" instead of "pay +919876543210 50"
"""
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.sql import func
from backend.database import Base


class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    owner_phone = Column(String(20), nullable=False, index=True)  # Who saved this contact
    nickname = Column(String(50), nullable=False)  # Lowercase name (e.g., "ansh")
    contact_phone = Column(String(20), nullable=False)  # The saved phone number
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Each user can only have one contact per nickname
    __table_args__ = (
        UniqueConstraint('owner_phone', 'nickname', name='uq_owner_nickname'),
    )
    
    def __repr__(self):
        return f"<Contact {self.owner_phone}: {self.nickname} -> {self.contact_phone}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "owner_phone": self.owner_phone,
            "nickname": self.nickname,
            "contact_phone": self.contact_phone,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
