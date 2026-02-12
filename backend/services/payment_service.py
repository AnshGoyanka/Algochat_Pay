"""
Payment service - Handle ALGO transfers
Demo-safe with retry logic and fallback support
"""
from sqlalchemy.orm import Session
from typing import Optional
import logging
from datetime import datetime
from backend.models.transaction import Transaction, TransactionStatus, TransactionType
from backend.algorand.client import algorand_client
from backend.services.wallet_service import wallet_service
from backend.utils.demo_safety import safe_demo_operation
from backend.utils.production_logging import event_logger

logger = logging.getLogger(__name__)


class PaymentService:
    """
    Handles all payment operations
    Coordinates between database and Algorand network
    """
    
    @safe_demo_operation("send_payment")
    def send_payment(
        self,
        db: Session,
        sender_phone: str,
        receiver_phone: str,
        amount: float,
        note: str = ""
    ) -> Transaction:
        """
        Send ALGO from one user to another (demo-safe with retry)
        
        Args:
            db: Database session
            sender_phone: Sender's phone number
            receiver_phone: Receiver's phone number
            amount: Amount in ALGO
            note: Optional transaction note
        
        Returns:
            Transaction record
        
        Raises:
            ValueError: If validation fails
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Get sender wallet
        sender = wallet_service.get_user_by_phone(db, sender_phone)
        if not sender:
            raise ValueError(f"Sender wallet not found: {sender_phone}")
        
        # Get receiver wallet (create if doesn't exist)
        receiver, _ = wallet_service.get_or_create_wallet(db, receiver_phone)
        
        # Check sender balance
        sender_balance = algorand_client.get_balance(sender.wallet_address)
        if sender_balance < amount + 0.001:  # Include fee
            raise ValueError(f"Insufficient balance. Have {sender_balance} ALGO, need {amount + 0.001}")
        
        # Get sender's private key for signing
        sender_private_key = wallet_service.get_private_key(db, sender_phone)
        
        # Log transaction initiation
        event_logger.transaction_initiated(
            sender_phone, 
            receiver_phone, 
            amount, 
            "SEND"
        )
        
        # Create transaction record (pending)
        transaction = Transaction(
            sender_phone=sender_phone,
            sender_address=sender.wallet_address,
            receiver_phone=receiver_phone,
            receiver_address=receiver.wallet_address,
            amount=amount,
            transaction_type=TransactionType.SEND,
            status=TransactionStatus.PENDING,
            note=note
        )
        
        db.add(transaction)
        db.commit()
        
        try:
            # Execute on Algorand network (with built-in retry)
            tx_id = algorand_client.send_payment(
                sender_private_key=sender_private_key,
                receiver_address=receiver.wallet_address,
                amount_algo=amount,
                note=note
            )
            
            # Update transaction record
            transaction.tx_id = tx_id
            transaction.status = TransactionStatus.CONFIRMED
            transaction.confirmed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(transaction)
            
            event_logger.transaction_completed(tx_id, sender_phone, amount)
            logger.info(f"Payment successful: {tx_id}")
            return transaction
            
        except Exception as e:
            # Mark as failed
            transaction.status = TransactionStatus.FAILED
            db.commit()
            
            event_logger.transaction_failed(str(e), sender_phone)
            logger.error(f"Payment failed: {e}")
            raise
    
    def send_payment_to_address(
        self,
        db: Session,
        sender_phone: str,
        receiver_address: str,
        amount: float,
        note: str = ""
    ) -> Transaction:
        """
        Send ALGO to an Algorand address (not necessarily a registered user)
        
        Args:
            db: Database session
            sender_phone: Sender's phone number
            receiver_address: Recipient's Algorand address
            amount: Amount in ALGO
            note: Optional transaction note
        
        Returns:
            Transaction record
        """
        # Validate amount
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Get sender wallet
        sender = wallet_service.get_user_by_phone(db, sender_phone)
        if not sender:
            raise ValueError(f"Sender wallet not found: {sender_phone}")
        
        # Check sender balance
        sender_balance = algorand_client.get_balance(sender.wallet_address)
        if sender_balance < amount + 0.001:
            raise ValueError(f"Insufficient balance")
        
        # Get sender's private key
        sender_private_key = wallet_service.get_private_key(db, sender_phone)
        
        # Create transaction record
        transaction = Transaction(
            sender_phone=sender_phone,
            sender_address=sender.wallet_address,
            receiver_address=receiver_address,
            amount=amount,
            transaction_type=TransactionType.SEND,
            status=TransactionStatus.PENDING,
            note=note
        )
        
        db.add(transaction)
        db.commit()
        
        try:
            # Execute on blockchain
            tx_id = algorand_client.send_payment(
                sender_private_key=sender_private_key,
                receiver_address=receiver_address,
                amount_algo=amount,
                note=note
            )
            
            # Update transaction
            transaction.tx_id = tx_id
            transaction.status = TransactionStatus.CONFIRMED
            transaction.confirmed_at = datetime.utcnow()
            
            db.commit()
            db.refresh(transaction)
            
            return transaction
            
        except Exception as e:
            transaction.status = TransactionStatus.FAILED
            db.commit()
            raise
    
    def get_transaction_history(
        self,
        db: Session,
        phone_number: str,
        limit: int = 20
    ) -> list[Transaction]:
        """
        Get transaction history for a user
        
        Args:
            db: Database session
            phone_number: User's phone number
            limit: Max number of transactions to return
        
        Returns:
            List of Transaction objects
        """
        transactions = db.query(Transaction).filter(
            (Transaction.sender_phone == phone_number) | 
            (Transaction.receiver_phone == phone_number)
        ).order_by(Transaction.timestamp.desc()).limit(limit).all()
        
        return transactions
    
    def get_transaction_by_id(self, db: Session, tx_id: str) -> Optional[Transaction]:
        """Get transaction by Algorand transaction ID"""
        return db.query(Transaction).filter(Transaction.tx_id == tx_id).first()


# Global service instance
payment_service = PaymentService()
