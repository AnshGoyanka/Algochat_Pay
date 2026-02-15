"""
Commitment Service - Business logic for payment commitments
Handles creation, locking, releasing, and social features
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from backend.models.commitment import (
    PaymentCommitment,
    CommitmentParticipant,
    CommitmentReminder,
    ReliabilityScore,
    CommitmentStatus,
    ParticipantStatus
)
from backend.models.user import User
from backend.services.escrow_service import escrow_service
from backend.services.wallet_service import wallet_service

logger = logging.getLogger(__name__)


class CommitmentService:
    """
    Handles payment lock commitments for trips, events, etc.
    Solves "I'll pay later" problem with blockchain escrow
    """
    
    def create_commitment(
        self,
        db: Session,
        organizer_phone: str,
        title: str,
        amount_per_person: float,
        total_participants: int,
        deadline: datetime,
        description: str = ""
    ) -> PaymentCommitment:
        """
        Create a new payment commitment
        
        Args:
            db: Database session
            organizer_phone: Organizer's phone number
            title: Commitment title (e.g., "Goa Trip")
            amount_per_person: Amount each person needs to lock
            total_participants: Expected number of participants
            deadline: When funds auto-release
            description: Optional description
        
        Returns:
            PaymentCommitment object
        """
        try:
            # Validate organizer exists
            organizer = wallet_service.get_user_by_phone(db, organizer_phone)
            if not organizer:
                raise ValueError("Organizer not found")
            
            # Create escrow account
            escrow_data = escrow_service.create_escrow_account()
            
            # Create commitment
            commitment = PaymentCommitment(
                organizer_phone=organizer_phone,
                title=title,
                description=description,
                amount_per_person=amount_per_person,
                total_participants=total_participants,
                deadline=deadline,
                escrow_address=escrow_data["address"],
                encrypted_escrow_key=escrow_data["private_key"],  # Store encrypted key in commitment
                status=CommitmentStatus.ACTIVE
            )
            
            db.add(commitment)
            db.commit()
            db.refresh(commitment)
            
            logger.info(f"Created commitment #{commitment.id}: {title}")
            return commitment
            
        except Exception as e:
            logger.error(f"Failed to create commitment: {e}")
            db.rollback()
            raise
    
    def add_participant(
        self,
        db: Session,
        commitment_id: int,
        phone: str
    ) -> CommitmentParticipant:
        """
        Add a participant to commitment
        
        Args:
            db: Database session
            commitment_id: Commitment ID
            phone: Participant's phone number
        
        Returns:
            CommitmentParticipant object
        """
        try:
            # Get commitment
            commitment = db.query(PaymentCommitment).filter(
                PaymentCommitment.id == commitment_id
            ).first()
            
            if not commitment:
                raise ValueError(f"Commitment not found: {commitment_id}")
            
            if not commitment.is_active:
                raise ValueError("Commitment is no longer active")
            
            # Check if already participant
            existing = db.query(CommitmentParticipant).filter(
                CommitmentParticipant.commitment_id == commitment_id,
                CommitmentParticipant.phone == phone
            ).first()
            
            if existing:
                return existing
            
            # Get participant's wallet
            user = wallet_service.get_user_by_phone(db, phone)
            wallet_address = user.wallet_address if user else None
            
            # Create participant
            participant = CommitmentParticipant(
                commitment_id=commitment_id,
                phone=phone,
                wallet_address=wallet_address,
                amount=commitment.amount_per_person,
                status=ParticipantStatus.INVITED
            )
            
            db.add(participant)
            db.commit()
            db.refresh(participant)
            
            logger.info(f"Added participant {phone} to commitment #{commitment_id}")
            return participant
            
        except Exception as e:
            logger.error(f"Failed to add participant: {e}")
            db.rollback()
            raise
    
    def lock_funds(
        self,
        db: Session,
        commitment_id: int,
        participant_phone: str
    ) -> CommitmentParticipant:
        """
        Lock participant's funds into escrow
        
        Args:
            db: Database session
            commitment_id: Commitment ID
            participant_phone: Participant's phone number
        
        Returns:
            Updated CommitmentParticipant
        """
        try:
            # Get commitment and participant
            commitment = db.query(PaymentCommitment).filter(
                PaymentCommitment.id == commitment_id
            ).first()
            
            if not commitment:
                raise ValueError(f"Commitment not found: {commitment_id}")
            
            if not commitment.is_active:
                raise ValueError("Commitment deadline has passed or is canceled")
            
            participant = db.query(CommitmentParticipant).filter(
                CommitmentParticipant.commitment_id == commitment_id,
                CommitmentParticipant.phone == participant_phone
            ).first()
            
            if not participant:
                # Auto-add if not already added
                participant = self.add_participant(db, commitment_id, participant_phone)
            
            if participant.is_locked:
                raise ValueError("Funds already locked")
            
            # Get participant's private key
            private_key = wallet_service.get_private_key(db, participant_phone)
            
            # Check balance
            user = wallet_service.get_user_by_phone(db, participant_phone)
            balance = wallet_service.get_balance(user.wallet_address)
            
            if balance < commitment.amount_per_person + 0.001:
                raise ValueError(f"Insufficient balance. Need {commitment.amount_per_person} ALGO")
            
            # Lock funds to escrow
            tx_id = escrow_service.lock_funds_to_escrow(
                participant_private_key=private_key,
                escrow_address=commitment.escrow_address,
                amount=commitment.amount_per_person,
                note=f"Locked for: {commitment.title}"
            )
            
            # Update participant status
            participant.status = ParticipantStatus.LOCKED
            participant.locked_at = datetime.utcnow()
            participant.lock_tx_id = tx_id
            
            # Update commitment totals
            commitment.participants_locked += 1
            commitment.total_locked += commitment.amount_per_person
            
            db.commit()
            db.refresh(participant)
            
            # Update reliability score
            self._update_reliability_score(db, participant_phone, "locked")
            
            logger.info(f"Locked {commitment.amount_per_person} ALGO for participant {participant_phone}")
            return participant
            
        except Exception as e:
            logger.error(f"Failed to lock funds: {e}")
            db.rollback()
            raise
    
    def release_commitment(
        self,
        db: Session,
        commitment_id: int
    ) -> str:
        """
        Release all locked funds to organizer
        Called when deadline passes
        
        Args:
            db: Database session
            commitment_id: Commitment ID
        
        Returns:
            Transaction ID
        """
        try:
            commitment = db.query(PaymentCommitment).filter(
                PaymentCommitment.id == commitment_id
            ).first()
            
            if not commitment:
                raise ValueError(f"Commitment not found: {commitment_id}")
            
            if commitment.status != CommitmentStatus.ACTIVE:
                raise ValueError("Commitment already processed")
            
            # Get escrow private key from commitment
            escrow_key = commitment.encrypted_escrow_key
            
            if not escrow_key:
                raise ValueError("Escrow key not found")
            
            # Get organizer wallet address
            organizer = wallet_service.get_user_by_phone(db, commitment.organizer_phone)
            
            # Release to organizer
            tx_id = escrow_service.batch_release_to_organizer(
                escrow_private_key=escrow_key,
                escrow_address=commitment.escrow_address,
                organizer_address=organizer.wallet_address,
                note=f"Released: {commitment.title}"
            )
            
            # Update commitment
            commitment.status = CommitmentStatus.COMPLETED
            commitment.released_at = datetime.utcnow()
            commitment.released_tx_id = tx_id
            
            # Update all locked participants
            locked_participants = db.query(CommitmentParticipant).filter(
                CommitmentParticipant.commitment_id == commitment_id,
                CommitmentParticipant.status == ParticipantStatus.LOCKED
            ).all()
            
            for participant in locked_participants:
                participant.status = ParticipantStatus.RELEASED
                participant.released_at = datetime.utcnow()
                participant.release_tx_id = tx_id
                self._update_reliability_score(db, participant.phone, "released")
            
            # Mark non-locked participants as missed
            missed_participants = db.query(CommitmentParticipant).filter(
                CommitmentParticipant.commitment_id == commitment_id,
                CommitmentParticipant.status == ParticipantStatus.INVITED
            ).all()
            
            for participant in missed_participants:
                participant.status = ParticipantStatus.MISSED
                self._update_reliability_score(db, participant.phone, "missed")
            
            db.commit()
            
            logger.info(f"Released commitment #{commitment_id}: {tx_id}")
            return tx_id
            
        except Exception as e:
            logger.error(f"Failed to release commitment: {e}")
            db.rollback()
            raise
    
    def cancel_commitment(
        self,
        db: Session,
        commitment_id: int,
        organizer_phone: str
    ) -> Dict[str, str]:
        """
        Cancel commitment and refund all participants
        
        Args:
            db: Database session
            commitment_id: Commitment ID
            organizer_phone: Organizer's phone (for authorization)
        
        Returns:
            Dict mapping participant phone to refund transaction ID
        """
        try:
            commitment = db.query(PaymentCommitment).filter(
                PaymentCommitment.id == commitment_id
            ).first()
            
            if not commitment:
                raise ValueError(f"Commitment not found: {commitment_id}")
            
            if commitment.organizer_phone != organizer_phone:
                raise ValueError("Only organizer can cancel commitment")
            
            if commitment.status != CommitmentStatus.ACTIVE:
                raise ValueError("Commitment already processed")
            
            # Get escrow private key from commitment
            escrow_key = commitment.encrypted_escrow_key
            
            if not escrow_key:
                raise ValueError("Escrow key not found")
            
            # Get all locked participants
            locked_participants = db.query(CommitmentParticipant).filter(
                CommitmentParticipant.commitment_id == commitment_id,
                CommitmentParticipant.status == ParticipantStatus.LOCKED
            ).all()
            
            # Prepare refund list
            refunds = [
                {
                    "address": p.wallet_address,
                    "amount": p.amount,
                    "phone": p.phone
                }
                for p in locked_participants
            ]
            
            # Batch refund
            results = escrow_service.batch_refund_to_participants(
                escrow_private_key=escrow_key,
                participants=refunds,
                note=f"Refund: {commitment.title} canceled"
            )
            
            # Update commitment
            commitment.status = CommitmentStatus.CANCELED
            
            # Update participants
            for participant in locked_participants:
                tx_id = results.get(participant.wallet_address, "ERROR")
                participant.status = ParticipantStatus.REFUNDED
                participant.release_tx_id = tx_id
            
            db.commit()
            
            logger.info(f"Canceled commitment #{commitment_id}")
            return {p.phone: results.get(p.wallet_address) for p in locked_participants}
            
        except Exception as e:
            logger.error(f"Failed to cancel commitment: {e}")
            db.rollback()
            raise
    
    def get_commitment_status(
        self,
        db: Session,
        commitment_id: int
    ) -> Dict:
        """
        Get detailed status of a commitment
        
        Returns:
            Dict with commitment details and participant status
        """
        commitment = db.query(PaymentCommitment).filter(
            PaymentCommitment.id == commitment_id
        ).first()
        
        if not commitment:
            raise ValueError(f"Commitment not found: {commitment_id}")
        
        participants = db.query(CommitmentParticipant).filter(
            CommitmentParticipant.commitment_id == commitment_id
        ).all()
        
        locked = [p for p in participants if p.is_locked]
        not_locked = [p for p in participants if p.status == ParticipantStatus.INVITED]
        
        return {
            "id": commitment.id,
            "title": commitment.title,
            "description": commitment.description,
            "amount_per_person": commitment.amount_per_person,
            "organizer": commitment.organizer_phone,
            "deadline": commitment.deadline,
            "status": commitment.status.value,
            "total_locked": commitment.total_locked,
            "participants_locked": commitment.participants_locked,
            "total_participants": commitment.total_participants,
            "completion_percentage": commitment.completion_percentage,
            "days_until_deadline": commitment.days_until_deadline,
            "locked_participants": [
                {
                    "phone": p.phone,
                    "amount": p.amount,
                    "locked_at": p.locked_at
                }
                for p in locked
            ],
            "pending_participants": [
                {
                    "phone": p.phone,
                    "amount": p.amount,
                    "reminder_count": p.reminder_count
                }
                for p in not_locked
            ]
        }
    
    def get_user_reliability(
        self,
        db: Session,
        phone: str
    ) -> Dict:
        """
        Get user's reliability score and history
        """
        score = db.query(ReliabilityScore).filter(
            ReliabilityScore.phone == phone
        ).first()
        
        if not score:
            # Create default score
            score = ReliabilityScore(phone=phone)
            db.add(score)
            db.commit()
            db.refresh(score)
        
        # Get recent commitments
        recent = db.query(CommitmentParticipant).filter(
            CommitmentParticipant.phone == phone
        ).order_by(CommitmentParticipant.invited_at.desc()).limit(5).all()
        
        return {
            "phone": phone,
            "score": score.score,
            "badge": score.badge,
            "reliability_percentage": score.reliability_percentage,
            "total_commitments": score.total_commitments,
            "fulfilled_on_time": score.fulfilled_on_time,
            "missed": score.missed,
            "recent_commitments": [
                {
                    "commitment_id": p.commitment_id,
                    "amount": p.amount,
                    "status": p.status.value,
                    "locked_at": p.locked_at
                }
                for p in recent
            ]
        }
    
    def _update_reliability_score(
        self,
        db: Session,
        phone: str,
        action: str
    ):
        """
        Update user's reliability score based on action
        
        Args:
            db: Database session
            phone: User's phone number
            action: "locked", "released", "missed"
        """
        try:
            score = db.query(ReliabilityScore).filter(
                ReliabilityScore.phone == phone
            ).first()
            
            if not score:
                score = ReliabilityScore(phone=phone)
                db.add(score)
            
            score.total_commitments += 1
            
            if action == "released":
                score.fulfilled_on_time += 1
            elif action == "missed":
                score.missed += 1
            
            # Recalculate score (weighted)
            if score.total_commitments > 0:
                score.score = int(
                    (score.fulfilled_on_time / score.total_commitments) * 100
                )
            
            score.updated_at = datetime.utcnow()
            db.commit()
            
        except Exception as e:
            logger.error(f"Failed to update reliability score: {e}")


# Singleton instance
commitment_service = CommitmentService()
