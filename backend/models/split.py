"""
Split payment models - Track bill splitting between users
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from backend.database import Base


class SplitStatus(str, enum.Enum):
    """Split payment status"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class SplitBill(Base):
    """
    Split bill/payment tracking
    Represents a bill that needs to be split among multiple people
    """
    __tablename__ = "split_bills"
    
    id = Column(Integer, primary_key=True, index=True)
    initiator_phone = Column(String(20), nullable=False, index=True)
    total_amount = Column(Float, nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(SplitStatus), default=SplitStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    payments = relationship("SplitPayment", back_populates="split_bill", cascade="all, delete-orphan")
    
    @property
    def num_participants(self):
        """Total number of participants (including initiator)"""
        return len(self.payments)
    
    @property
    def amount_per_person(self):
        """Amount each person should pay"""
        if self.num_participants == 0:
            return 0
        return self.total_amount / self.num_participants
    
    @property
    def total_collected(self):
        """Total amount collected so far"""
        return sum(p.amount for p in self.payments if p.is_paid)
    
    @property
    def is_fully_paid(self):
        """Check if all participants have paid"""
        return all(p.is_paid for p in self.payments)


class SplitPayment(Base):
    """
    Individual payment within a split bill
    Tracks each participant's share and payment status
    """
    __tablename__ = "split_payments"
    
    id = Column(Integer, primary_key=True, index=True)
    split_bill_id = Column(Integer, ForeignKey("split_bills.id"), nullable=False)
    participant_phone = Column(String(20), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    is_paid = Column(Boolean, default=False)
    tx_id = Column(String(100), nullable=True)  # Algorand transaction ID
    paid_at = Column(DateTime, nullable=True)
    
    # Relationships
    split_bill = relationship("SplitBill", back_populates="payments")
