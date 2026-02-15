"""
Transaction model - Records all ALGO transfers
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from backend.database import Base


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"


class TransactionType(str, enum.Enum):
    SEND = "send"
    RECEIVE = "receive"
    SPLIT = "split"
    FUND = "fund"
    TICKET = "ticket"


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    tx_id = Column(String(100), unique=True, index=True)  # Algorand transaction ID
    sender_phone = Column(String(20), index=True, nullable=False)
    sender_address = Column(String(58), nullable=False)
    receiver_phone = Column(String(20), index=True, nullable=True)
    receiver_address = Column(String(58), nullable=True)
    amount = Column(Float, nullable=False)  # ALGO amount
    fee = Column(Float, default=0.001)  # Network fee
    transaction_type = Column(SQLEnum(TransactionType), default=TransactionType.SEND)
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    note = Column(String(500))  # Transaction memo
    split_group_id = Column(String(100))  # For bill splitting
    fund_id = Column(Integer)  # Link to fundraising pool
    
    # Privacy-enhanced fields
    merchant_id = Column(String(20), index=True)  # Link to merchants table (M12345)
    payment_ref = Column(String(20), index=True)   # Human-friendly payment ID (P67890)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Transaction {self.tx_id[:8]}... {self.amount} ALGO>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "tx_id": self.tx_id,
            "sender_phone": self.sender_phone,
            "receiver_phone": self.receiver_phone,
            "amount": self.amount,
            "fee": self.fee,
            "type": self.transaction_type.value,
            "status": self.status.value,
            "note": self.note,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
