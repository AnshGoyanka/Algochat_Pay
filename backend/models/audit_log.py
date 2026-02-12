"""
Database model for audit logs
Tracks security-sensitive operations
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from backend.database import Base


class AuditLog(Base):
    """
    Audit log for security tracking
    Records all critical operations for compliance and forensics
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Who
    user_phone = Column(String, index=True, nullable=True)  # May be null for system events
    user_address = Column(String, index=True, nullable=True)
    
    # What
    event_type = Column(String, index=True, nullable=False)  # e.g., "wallet_created", "payment_sent"
    action = Column(String, nullable=False)  # Human-readable action
    
    # When
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Where
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Details
    details = Column(JSON, nullable=True)  # Additional context
    
    # Result
    success = Column(String, nullable=False)  # "success", "failure", "partial"
    error_message = Column(Text, nullable=True)
    
    # Correlation
    correlation_id = Column(String, index=True, nullable=True)  # Links related events
    
    def __repr__(self):
        return f"<AuditLog {self.event_type} by {self.user_phone} at {self.timestamp}>"
