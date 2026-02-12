"""
Fundraising pool models
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.database import Base


class Fund(Base):
    __tablename__ = "funds"
    
    id = Column(Integer, primary_key=True, index=True)
    creator_phone = Column(String(20), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(String(1000))
    goal_amount = Column(Float, nullable=False)  # Target in ALGO
    current_amount = Column(Float, default=0.0)  # Current raised
    contract_app_id = Column(Integer)  # Algorand smart contract ID
    is_active = Column(Boolean, default=True)
    is_goal_met = Column(Boolean, default=False)
    deadline = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True))
    
    # Relationships
    contributions = relationship("FundContribution", back_populates="fund")
    
    def __repr__(self):
        return f"<Fund {self.title} - {self.current_amount}/{self.goal_amount} ALGO>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "creator_phone": self.creator_phone,
            "title": self.title,
            "goal_amount": self.goal_amount,
            "current_amount": self.current_amount,
            "is_goal_met": self.is_goal_met,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class FundContribution(Base):
    __tablename__ = "fund_contributions"
    
    id = Column(Integer, primary_key=True, index=True)
    fund_id = Column(Integer, ForeignKey("funds.id"), nullable=False)
    contributor_phone = Column(String(20), nullable=False)
    amount = Column(Float, nullable=False)
    tx_id = Column(String(100), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    fund = relationship("Fund", back_populates="contributions")
    
    def __repr__(self):
        return f"<Contribution {self.amount} ALGO to Fund {self.fund_id}>"
