"""
Fund service - Fundraising pools with smart contracts
"""
from sqlalchemy.orm import Session
from typing import Optional
import logging
from datetime import datetime, timedelta
from backend.models.fund import Fund, FundContribution
from backend.models.transaction import Transaction, TransactionStatus, TransactionType
from backend.algorand.client import algorand_client
from backend.services.wallet_service import wallet_service

logger = logging.getLogger(__name__)


class FundService:
    """
    Manages fundraising pools
    Future: Will integrate with smart contracts for automatic refunds
    """
    
    def create_fund(
        self,
        db: Session,
        creator_phone: str,
        title: str,
        goal_amount: float,
        description: str = "",
        deadline_hours: int = 168  # 7 days default
    ) -> Fund:
        """
        Create a new fundraising pool
        
        Args:
            db: Database session
            creator_phone: Creator's phone number
            title: Fund title
            goal_amount: Target amount in ALGO
            description: Fund description
            deadline_hours: Hours until deadline
        
        Returns:
            Fund record
        """
        # Validate inputs
        if goal_amount <= 0:
            raise ValueError("Goal amount must be positive")
        
        # Get or create creator wallet
        creator, _ = wallet_service.get_or_create_wallet(db, creator_phone)
        
        # Calculate deadline
        deadline = datetime.utcnow() + timedelta(hours=deadline_hours)
        
        # Create fund record
        fund = Fund(
            creator_phone=creator_phone,
            title=title,
            description=description,
            goal_amount=goal_amount,
            deadline=deadline
        )
        
        db.add(fund)
        db.commit()
        db.refresh(fund)
        
        logger.info(f"Created fund: {title} (Goal: {goal_amount} ALGO)")
        return fund
    
    def contribute_to_fund(
        self,
        db: Session,
        fund_id: int,
        contributor_phone: str,
        amount: float
    ) -> FundContribution:
        """
        Contribute ALGO to a fundraising pool
        
        Args:
            db: Database session
            fund_id: Fund ID
            contributor_phone: Contributor's phone number
            amount: Contribution amount in ALGO
        
        Returns:
            FundContribution record
        """
        # Get fund
        fund = db.query(Fund).filter(Fund.id == fund_id).first()
        if not fund:
            raise ValueError(f"Fund not found: {fund_id}")
        
        if not fund.is_active:
            raise ValueError("Fund is no longer active")
        
        # Check deadline
        if fund.deadline and datetime.utcnow() > fund.deadline:
            raise ValueError("Fund deadline has passed")
        
        # Validate amount
        if amount <= 0:
            raise ValueError("Contribution must be positive")
        
        # Get contributor wallet
        contributor, _ = wallet_service.get_or_create_wallet(db, contributor_phone)
        
        # Get creator wallet (fund escrow)
        creator = wallet_service.get_user_by_phone(db, fund.creator_phone)
        
        # Check contributor balance
        contributor_balance = algorand_client.get_balance(contributor.wallet_address)
        if contributor_balance < amount + 0.001:
            raise ValueError(f"Insufficient balance")
        
        # Get contributor's private key
        contributor_private_key = wallet_service.get_private_key(db, contributor_phone)
        
        try:
            # Send ALGO to fund creator (escrow)
            tx_id = algorand_client.send_payment(
                sender_private_key=contributor_private_key,
                receiver_address=creator.wallet_address,
                amount_algo=amount,
                note=f"Fund: {fund.title}"
            )
            
            # Create contribution record
            contribution = FundContribution(
                fund_id=fund_id,
                contributor_phone=contributor_phone,
                amount=amount,
                tx_id=tx_id
            )
            
            db.add(contribution)
            
            # Update fund totals
            fund.current_amount += amount
            
            # Check if goal met
            if fund.current_amount >= fund.goal_amount:
                fund.is_goal_met = True
                logger.info(f"Fund {fund.title} reached goal!")
            
            # Create transaction record
            transaction = Transaction(
                tx_id=tx_id,
                sender_phone=contributor_phone,
                sender_address=contributor.wallet_address,
                receiver_phone=fund.creator_phone,
                receiver_address=creator.wallet_address,
                amount=amount,
                transaction_type=TransactionType.FUND,
                status=TransactionStatus.CONFIRMED,
                note=f"Fund contribution: {fund.title}",
                fund_id=fund_id,
                confirmed_at=datetime.utcnow()
            )
            
            db.add(transaction)
            db.commit()
            db.refresh(contribution)
            
            logger.info(f"Contribution {amount} ALGO to fund {fund_id}")
            return contribution
            
        except Exception as e:
            logger.error(f"Contribution failed: {e}")
            raise
    
    def get_fund_by_id(self, db: Session, fund_id: int) -> Optional[Fund]:
        """Get fund by ID"""
        return db.query(Fund).filter(Fund.id == fund_id).first()
    
    def get_fund_details(self, db: Session, fund_id: int) -> dict:
        """
        Get comprehensive fund details
        
        Returns:
            Dict with fund info and contributions
        """
        fund = self.get_fund_by_id(db, fund_id)
        
        if not fund:
            raise ValueError(f"Fund not found: {fund_id}")
        
        # Get all contributions
        contributions = db.query(FundContribution).filter(
            FundContribution.fund_id == fund_id
        ).all()
        
        return {
            "id": fund.id,
            "title": fund.title,
            "description": fund.description,
            "goal_amount": fund.goal_amount,
            "current_amount": fund.current_amount,
            "percentage": (fund.current_amount / fund.goal_amount * 100) if fund.goal_amount > 0 else 0,
            "is_goal_met": fund.is_goal_met,
            "is_active": fund.is_active,
            "creator_phone": fund.creator_phone,
            "deadline": fund.deadline.isoformat() if fund.deadline else None,
            "created_at": fund.created_at.isoformat() if fund.created_at else None,
            "contributions_count": len(contributions),
            "contributors": [
                {
                    "phone": c.contributor_phone,
                    "amount": c.amount,
                    "timestamp": c.created_at.isoformat() if c.created_at else None
                }
                for c in contributions
            ]
        }
    
    def list_active_funds(self, db: Session) -> list[Fund]:
        """Get all active fundraising pools"""
        return db.query(Fund).filter(Fund.is_active == True).all()
    
    def close_fund(self, db: Session, fund_id: int) -> Fund:
        """
        Close a fundraising fund
        
        Args:
            db: Database session
            fund_id: Fund ID
        
        Returns:
            Updated Fund record
        """
        fund = self.get_fund_by_id(db, fund_id)
        
        if not fund:
            raise ValueError(f"Fund not found: {fund_id}")
        
        fund.is_active = False
        fund.closed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(fund)
        
        logger.info(f"Closed fund: {fund.title}")
        return fund


# Global service instance
fund_service = FundService()
