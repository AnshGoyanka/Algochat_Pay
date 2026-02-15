"""
Payment Commitment Models - Lock funds for future payments
Solves "I'll pay later" problem with social accountability
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.database import Base


class CommitmentStatus(enum.Enum):
    """Status of a payment commitment"""
    ACTIVE = "active"  # Currently accepting locks
    COMPLETED = "completed"  # All participants paid, funds released
    CANCELED = "canceled"  # Organizer canceled, funds refunded
    EXPIRED = "expired"  # Deadline passed, partial payments


class ParticipantStatus(enum.Enum):
    """Status of individual participant in commitment"""
    INVITED = "invited"  # Invited but not locked yet
    LOCKED = "locked"  # Funds locked in escrow
    RELEASED = "released"  # Funds released to organizer
    REFUNDED = "refunded"  # Funds refunded to participant
    MISSED = "missed"  # Deadline passed without locking


class PaymentCommitment(Base):
    """
    Main commitment - created by organizer
    Example: "Goa Trip - 500 ALGO per person"
    """
    __tablename__ = "payment_commitments"
    
    id = Column(Integer, primary_key=True)
    
    # Organizer info
    organizer_phone = Column(String(20), nullable=False)
    
    # Commitment details
    title = Column(String(200), nullable=False)  # "Goa Trip"
    description = Column(Text)
    amount_per_person = Column(Float, nullable=False)
    
    # Participants
    total_participants = Column(Integer, nullable=False)  # Expected number
    
    # Timeline
    deadline = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Smart contract
    escrow_address = Column(String(100))  # Algorand escrow address
    escrow_app_id = Column(Integer)  # Smart contract app ID
    encrypted_escrow_key = Column(String(500))  # Encrypted private key for escrow
    
    # Status
    status = Column(SQLEnum(CommitmentStatus), default=CommitmentStatus.ACTIVE)
    
    # Totals
    total_locked = Column(Float, default=0.0)  # Sum of locked funds
    participants_locked = Column(Integer, default=0)  # Count of locked participants
    
    # Release info
    released_at = Column(DateTime)
    released_tx_id = Column(String(100))
    
    # Relationships
    participants = relationship("CommitmentParticipant", back_populates="commitment", cascade="all, delete-orphan")
    reminders = relationship("CommitmentReminder", back_populates="commitment", cascade="all, delete-orphan")
    
    @property
    def is_active(self):
        """Check if commitment is still active"""
        return self.status == CommitmentStatus.ACTIVE and datetime.utcnow() < self.deadline
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage"""
        if self.total_participants == 0:
            return 0
        return int((self.participants_locked / self.total_participants) * 100)
    
    @property
    def is_fully_committed(self):
        """Check if all participants have locked funds"""
        return self.participants_locked >= self.total_participants
    
    @property
    def days_until_deadline(self):
        """Days remaining until deadline"""
        if datetime.utcnow() > self.deadline:
            return 0
        delta = self.deadline - datetime.utcnow()
        return delta.days


class CommitmentParticipant(Base):
    """
    Individual participant in a commitment
    Tracks lock status and reliability
    """
    __tablename__ = "commitment_participants"
    
    id = Column(Integer, primary_key=True)
    commitment_id = Column(Integer, ForeignKey("payment_commitments.id"), nullable=False)
    
    # Participant info
    phone = Column(String(20), nullable=False)
    wallet_address = Column(String(100))
    
    # Lock info
    amount = Column(Float, nullable=False)
    status = Column(SQLEnum(ParticipantStatus), default=ParticipantStatus.INVITED)
    
    # Timestamps
    invited_at = Column(DateTime, default=datetime.utcnow)
    locked_at = Column(DateTime)
    released_at = Column(DateTime)
    
    # Transaction info
    lock_tx_id = Column(String(100))  # Transaction ID for locking funds
    release_tx_id = Column(String(100))  # Transaction ID for release/refund
    
    # Social features
    reminder_count = Column(Integer, default=0)
    last_reminded_at = Column(DateTime)
    
    # Relationships
    commitment = relationship("PaymentCommitment", back_populates="participants")
    
    @property
    def is_locked(self):
        """Check if participant has locked funds"""
        return self.status == ParticipantStatus.LOCKED
    
    @property
    def is_overdue(self):
        """Check if participant missed deadline"""
        return self.status == ParticipantStatus.MISSED


class CommitmentReminder(Base):
    """
    Automated reminders for participants
    Example: "Rahul, lock funds for Goa Trip - 2 days left!"
    """
    __tablename__ = "commitment_reminders"
    
    id = Column(Integer, primary_key=True)
    commitment_id = Column(Integer, ForeignKey("payment_commitments.id"), nullable=False)
    
    # Reminder config
    participant_phone = Column(String(20), nullable=False)
    hours_before_deadline = Column(Integer, nullable=False)  # 48, 24, 12, etc.
    
    # Status
    sent = Column(Boolean, default=False)
    sent_at = Column(DateTime)
    
    # Relationships
    commitment = relationship("PaymentCommitment", back_populates="reminders")


class ReliabilityScore(Base):
    """
    Track user's payment reliability over time
    Used for social accountability
    """
    __tablename__ = "reliability_scores"
    
    id = Column(Integer, primary_key=True)
    phone = Column(String(20), unique=True, nullable=False)
    
    # Commitment statistics
    total_commitments = Column(Integer, default=0)
    fulfilled_on_time = Column(Integer, default=0)
    fulfilled_late = Column(Integer, default=0)
    missed = Column(Integer, default=0)
    
    # Score (0-100)
    score = Column(Integer, default=100)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def reliability_percentage(self):
        """Calculate reliability as percentage"""
        if self.total_commitments == 0:
            return 100
        return int((self.fulfilled_on_time / self.total_commitments) * 100)
    
    @property
    def badge(self):
        """Get reliability badge emoji"""
        if self.score >= 95:
            return "💎"  # Diamond - Highly reliable
        elif self.score >= 85:
            return "🏆"  # Trophy - Very reliable
        elif self.score >= 70:
            return "⭐"  # Star - Reliable
        elif self.score >= 50:
            return "🔵"  # Blue - Average
        else:
            return "⚠️"  # Warning - Unreliable
