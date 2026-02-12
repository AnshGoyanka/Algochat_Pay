"""
Audit logging service
Records security-sensitive operations to database
"""
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from backend.models.audit_log import AuditLog
from backend.utils.production_logging import ProductionLogger, correlation_id

logger = ProductionLogger.get_logger(__name__)


class AuditService:
    """
    Service for audit logging
    Tracks all security-relevant operations
    """
    
    def log_event(
        self,
        db: Session,
        event_type: str,
        action: str,
        success: bool,
        user_phone: Optional[str] = None,
        user_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Log an audit event
        
        Args:
            db: Database session
            event_type: Type of event (e.g., "wallet_created", "payment_sent")
            action: Human-readable action description
            success: Whether operation succeeded
            user_phone: User's phone number
            user_address: User's wallet address
            details: Additional context (JSON)
            error_message: Error message if failed
            ip_address: User's IP address
            user_agent: User agent string
        
        Returns:
            Created audit log record
        """
        try:
            audit_log = AuditLog(
                user_phone=user_phone,
                user_address=user_address,
                event_type=event_type,
                action=action,
                success="success" if success else "failure",
                details=details,
                error_message=error_message,
                ip_address=ip_address,
                user_agent=user_agent,
                correlation_id=correlation_id.get()
            )
            
            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)
            
            logger.info(
                f"Audit log created: {event_type}",
                extra={
                    "event_type": event_type,
                    "user_phone": user_phone,
                    "success": success
                }
            )
            
            return audit_log
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}", exc_info=True)
            # Don't fail the main operation if audit logging fails
            db.rollback()
            raise
    
    def log_wallet_created(
        self,
        db: Session,
        phone_number: str,
        wallet_address: str,
        ip_address: Optional[str] = None
    ):
        """Log wallet creation event"""
        return self.log_event(
            db=db,
            event_type="wallet_created",
            action=f"Created wallet for {phone_number}",
            success=True,
            user_phone=phone_number,
            user_address=wallet_address,
            details={"wallet_address": wallet_address},
            ip_address=ip_address
        )
    
    def log_payment_sent(
        self,
        db: Session,
        sender_phone: str,
        receiver_phone: str,
        amount: float,
        tx_id: str,
        success: bool = True,
        error: Optional[str] = None,
        ip_address: Optional[str] = None
    ):
        """Log payment transaction"""
        return self.log_event(
            db=db,
            event_type="payment_sent",
            action=f"Sent {amount} ALGO to {receiver_phone}",
            success=success,
            user_phone=sender_phone,
            details={
                "receiver": receiver_phone,
                "amount": amount,
                "tx_id": tx_id
            },
            error_message=error,
            ip_address=ip_address
        )
    
    def log_security_event(
        self,
        db: Session,
        event_type: str,
        description: str,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """Log security-related events (rate limits, injection attempts, etc.)"""
        return self.log_event(
            db=db,
            event_type=event_type,
            action=description,
            success=False,  # Security events are typically failures
            details=details,
            ip_address=ip_address
        )
    
    def get_user_audit_trail(
        self,
        db: Session,
        phone_number: str,
        limit: int = 50
    ) -> list[AuditLog]:
        """
        Get audit trail for a user
        
        Args:
            db: Database session
            phone_number: User's phone number
            limit: Maximum number of records to return
        
        Returns:
            List of audit log records
        """
        return db.query(AuditLog).filter(
            AuditLog.user_phone == phone_number
        ).order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).all()


# Global audit service instance
audit_service = AuditService()
