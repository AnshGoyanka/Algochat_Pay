"""
Split payment service - Handle bill splitting between users
"""
from sqlalchemy.orm import Session
from typing import List, Dict
import logging
from datetime import datetime

from backend.models.split import SplitBill, SplitPayment, SplitStatus
from backend.models.transaction import Transaction, TransactionStatus, TransactionType
from backend.services.wallet_service import wallet_service
from backend.services.payment_service import payment_service
from backend.services.merchant_service import merchant_service

logger = logging.getLogger(__name__)


class SplitPaymentService:
    """
    Service for managing split payments
    Allows users to split bills among multiple people
    """
    
    def create_split_bill(
        self,
        db: Session,
        initiator_phone: str,
        total_amount: float,
        description: str,
        participant_phones: List[str]
    ) -> SplitBill:
        """
        Create a new split bill
        
        Args:
            db: Database session
            initiator_phone: Phone number of person creating the split
            total_amount: Total amount to split
            description: What the bill is for
            participant_phones: List of participant phone numbers (excluding initiator)
        
        Returns:
            SplitBill record
        """
        # Validate inputs
        if total_amount <= 0:
            raise ValueError("Total amount must be positive")
        
        if not participant_phones:
            raise ValueError("At least one participant required")
        
        # Remove duplicates
        participant_phones = list(set(participant_phones))
        
        # Ensure initiator is not in participant list
        participant_phones = [p for p in participant_phones if p != initiator_phone]
        
        # Calculate per-person amount (initiator + participants)
        all_people = [initiator_phone] + participant_phones
        num_people = len(all_people)
        per_person = total_amount / num_people
        
        # Create split bill
        split_bill = SplitBill(
            initiator_phone=initiator_phone,
            total_amount=total_amount,
            description=description,
            status=SplitStatus.PENDING
        )
        
        db.add(split_bill)
        db.flush()  # Get the ID
        
        # Create payment records for all participants (including initiator)
        for phone in all_people:
            split_payment = SplitPayment(
                split_bill_id=split_bill.id,
                participant_phone=phone,
                amount=per_person,
                is_paid=False  # All start as unpaid
            )
            db.add(split_payment)
        
        db.commit()
        db.refresh(split_bill)
        
        logger.info(f"Split bill created: {split_bill.id} by {initiator_phone}")
        
        # Send notifications to all participants (excluding initiator)
        try:
            from backend.services.notification_service import notification_service
            for phone in participant_phones:
                notification_service.notify_split_bill_created(
                    participant_phone=phone,
                    initiator_phone=initiator_phone,
                    split_id=split_bill.id,
                    amount_per_person=per_person,
                    description=description
                )
        except Exception as notify_error:
            logger.warning(f"Failed to send split bill notifications: {notify_error}")
        
        return split_bill
    
    def pay_split_share(
        self,
        db: Session,
        split_bill_id: int,
        participant_phone: str
    ) -> Dict:
        """
        Pay your share of a split bill
        
        Args:
            db: Database session
            split_bill_id: Split bill ID
            participant_phone: Phone number of person paying
        
        Returns:
            Dict with payment details
        """
        # Get split bill
        split_bill = db.query(SplitBill).filter(SplitBill.id == split_bill_id).first()
        
        if not split_bill:
            raise ValueError(f"Split bill not found: {split_bill_id}")
        
        if split_bill.status != SplitStatus.PENDING:
            raise ValueError(f"Split bill is {split_bill.status.value}")
        
        # Get participant's payment record
        split_payment = db.query(SplitPayment).filter(
            SplitPayment.split_bill_id == split_bill_id,
            SplitPayment.participant_phone == participant_phone
        ).first()
        
        if not split_payment:
            raise ValueError(f"You are not a participant in this split bill")
        
        if split_payment.is_paid:
            raise ValueError(f"You have already paid your share")
        
        # Get participant wallet
        participant, _ = wallet_service.get_or_create_wallet(db, participant_phone)
        
        # Get initiator wallet (they receive the payment)
        initiator, _ = wallet_service.get_or_create_wallet(db, split_bill.initiator_phone)
        
        # Check participant balance
        from backend.algorand.client import algorand_client
        participant_balance = algorand_client.get_balance(participant.wallet_address)
        
        if participant_balance < split_payment.amount + 0.001:
            raise ValueError(f"Insufficient balance. Need {split_payment.amount} ALGO + fees")
        
        # Get participant's private key
        participant_private_key = wallet_service.get_private_key(db, participant_phone)
        
        try:
            # Send payment to initiator
            tx_id = algorand_client.send_payment(
                sender_private_key=participant_private_key,
                receiver_address=initiator.wallet_address,
                amount_algo=split_payment.amount,
                note=f"Split: {split_bill.description[:50]}"
            )
            
            # Mark as paid
            split_payment.is_paid = True
            split_payment.tx_id = tx_id
            split_payment.paid_at = datetime.utcnow()
            
            # Generate payment reference
            payment_ref = merchant_service.generate_payment_ref()
            
            # Create transaction record
            transaction = Transaction(
                tx_id=tx_id,
                sender_phone=participant_phone,
                sender_address=participant.wallet_address,
                receiver_phone=split_bill.initiator_phone,
                receiver_address=initiator.wallet_address,
                amount=split_payment.amount,
                transaction_type=TransactionType.SPLIT,
                status=TransactionStatus.CONFIRMED,
                note=f"Split payment: {split_bill.description}",
                payment_ref=payment_ref,
                confirmed_at=datetime.utcnow()
            )
            
            db.add(transaction)
            
            # Check if all paid
            if split_bill.is_fully_paid:
                split_bill.status = SplitStatus.COMPLETED
                split_bill.completed_at = datetime.utcnow()
                logger.info(f"Split bill {split_bill_id} fully paid!")
            
            db.commit()
            
            # Send notification to initiator
            try:
                from backend.services.notification_service import notification_service
                notification_service.notify_split_payment_received(
                    initiator_phone=split_bill.initiator_phone,
                    participant_phone=participant_phone,
                    amount=split_payment.amount,
                    split_id=split_bill_id,
                    is_fully_paid=split_bill.is_fully_paid
                )
            except Exception as notify_error:
                logger.warning(f"Failed to send split payment notification: {notify_error}")
            
            return {
                "success": True,
                "split_bill_id": split_bill_id,
                "amount_paid": split_payment.amount,
                "tx_id": tx_id,
                "is_fully_paid": split_bill.is_fully_paid,
                "total_collected": split_bill.total_collected,
                "total_amount": split_bill.total_amount
            }
            
        except Exception as e:
            logger.error(f"Split payment failed: {e}")
            raise
    
    def get_split_bill(self, db: Session, split_bill_id: int) -> SplitBill:
        """Get split bill by ID"""
        return db.query(SplitBill).filter(SplitBill.id == split_bill_id).first()
    
    def get_split_bill_details(self, db: Session, split_bill_id: int) -> Dict:
        """
        Get comprehensive split bill details
        
        Returns:
            Dict with split bill info and payment statuses
        """
        split_bill = self.get_split_bill(db, split_bill_id)
        
        if not split_bill:
            raise ValueError(f"Split bill not found: {split_bill_id}")
        
        # Get all payment records
        payments = db.query(SplitPayment).filter(
            SplitPayment.split_bill_id == split_bill_id
        ).all()
        
        return {
            "id": split_bill.id,
            "initiator_phone": split_bill.initiator_phone,
            "total_amount": split_bill.total_amount,
            "description": split_bill.description,
            "status": split_bill.status.value,
            "amount_per_person": split_bill.amount_per_person,
            "total_collected": split_bill.total_collected,
            "is_fully_paid": split_bill.is_fully_paid,
            "created_at": split_bill.created_at.isoformat() if split_bill.created_at else None,
            "payments": [
                {
                    "phone": p.participant_phone,
                    "amount": p.amount,
                    "is_paid": p.is_paid,
                    "tx_id": p.tx_id,
                    "paid_at": p.paid_at.isoformat() if p.paid_at else None
                }
                for p in payments
            ]
        }
    
    def get_my_split_bills(self, db: Session, phone: str) -> List[SplitBill]:
        """
        Get all split bills involving a user (as initiator or participant)
        """
        # Get as initiator
        initiator_bills = db.query(SplitBill).filter(
            SplitBill.initiator_phone == phone,
            SplitBill.status == SplitStatus.PENDING
        ).all()
        
        # Get as participant
        participant_payments = db.query(SplitPayment).filter(
            SplitPayment.participant_phone == phone,
            SplitPayment.is_paid == False
        ).all()
        
        participant_bills = [p.split_bill for p in participant_payments if p.split_bill.status == SplitStatus.PENDING]
        
        # Combine and deduplicate
        all_bills = {bill.id: bill for bill in initiator_bills + participant_bills}
        
        return list(all_bills.values())


# Global service instance
split_service = SplitPaymentService()
