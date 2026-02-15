"""
Merchant service - Privacy-enhanced payment management
Generates payment references and manages merchant identities
"""
from sqlalchemy.orm import Session
import logging
import secrets
import string
from typing import Optional, Dict
from backend.models.merchant import Merchant, MerchantType

logger = logging.getLogger(__name__)


class MerchantService:
    """
    Manages merchant accounts for privacy-enhanced payments
    """
    
    def generate_merchant_id(self) -> str:
        """Generate unique merchant ID (M12345)"""
        # Generate 5-digit number
        number = ''.join(secrets.choice(string.digits) for _ in range(5))
        return f"M{number}"
    
    def generate_payment_ref(self) -> str:
        """Generate unique payment reference (P67890)"""
        # Generate 5-digit number
        number = ''.join(secrets.choice(string.digits) for _ in range(5))
        return f"P{number}"
    
    def create_merchant(
        self,
        db: Session,
        merchant_name: str,
        wallet_address: str,
        merchant_type: MerchantType,
        phone_number: str = None,
        description: str = None,
        event_id: int = None,
        fund_id: int = None
    ) -> Merchant:
        """
        Create a new merchant account
        
        Args:
            db: Database session
            merchant_name: Display name
            wallet_address: Algorand wallet address
            merchant_type: Type of merchant
            phone_number: Optional phone number
            description: Optional description
            event_id: Optional link to event
            fund_id: Optional link to fund
        
        Returns:
            Merchant object
        """
        try:
            # Generate unique merchant ID
            merchant_id = self.generate_merchant_id()
            
            # Ensure uniqueness
            while db.query(Merchant).filter(Merchant.merchant_id == merchant_id).first():
                merchant_id = self.generate_merchant_id()
            
            merchant = Merchant(
                merchant_id=merchant_id,
                merchant_name=merchant_name,
                merchant_type=merchant_type,
                wallet_address=wallet_address,
                phone_number=phone_number,
                description=description,
                event_id=event_id,
                fund_id=fund_id,
                is_active=True
            )
            
            db.add(merchant)
            db.commit()
            db.refresh(merchant)
            
            logger.info(f"Created merchant: {merchant_id} - {merchant_name}")
            return merchant
            
        except Exception as e:
            logger.error(f"Merchant creation failed: {e}")
            db.rollback()
            raise
    
    def get_merchant_by_id(self, db: Session, merchant_id: str) -> Optional[Merchant]:
        """Get merchant by merchant_id"""
        return db.query(Merchant).filter(
            Merchant.merchant_id == merchant_id,
            Merchant.is_active == True
        ).first()
    
    def get_merchant_by_event(self, db: Session, event_id: int) -> Optional[Merchant]:
        """Get merchant for an event"""
        return db.query(Merchant).filter(
            Merchant.event_id == event_id,
            Merchant.is_active == True
        ).first()
    
    def get_merchant_by_fund(self, db: Session, fund_id: int) -> Optional[Merchant]:
        """Get merchant for a fundraiser"""
        return db.query(Merchant).filter(
            Merchant.fund_id == fund_id,
            Merchant.is_active == True
        ).first()
    
    def get_merchant_by_wallet(self, db: Session, wallet_address: str) -> Optional[Merchant]:
        """Get merchant by wallet address"""
        return db.query(Merchant).filter(
            Merchant.wallet_address == wallet_address,
            Merchant.is_active == True
        ).first()
    
    def get_merchant_info(self, db: Session, merchant_id: str) -> Optional[Dict]:
        """
        Get merchant display information
        
        Returns:
            Dict with merchant_id, name, type, description
        """
        merchant = self.get_merchant_by_id(db, merchant_id)
        if not merchant:
            return None
        
        return {
            "merchant_id": merchant.merchant_id,
            "name": merchant.merchant_name,
            "type": merchant.merchant_type.value,
            "description": merchant.description
        }
    
    def create_merchant_for_event(
        self,
        db: Session,
        event_id: int,
        event_name: str,
        organizer_name: str,
        organizer_wallet: str
    ) -> Merchant:
        """
        Create merchant account for event organizer
        
        Args:
            db: Database session
            event_id: Event ID
            event_name: Event name
            organizer_name: Organizer display name
            organizer_wallet: Organizer's wallet address
        
        Returns:
            Merchant object
        """
        return self.create_merchant(
            db=db,
            merchant_name=f"{organizer_name}",
            wallet_address=organizer_wallet,
            merchant_type=MerchantType.EVENT_ORGANIZER,
            description=f"Event organizer for {event_name}",
            event_id=event_id
        )
    
    def create_merchant_for_fund(
        self,
        db: Session,
        fund_id: int,
        fund_title: str,
        beneficiary_name: str,
        beneficiary_wallet: str
    ) -> Merchant:
        """
        Create merchant account for fundraiser
        
        Args:
            db: Database session
            fund_id: Fund ID
            fund_title: Fund title
            beneficiary_name: Beneficiary display name
            beneficiary_wallet: Beneficiary's wallet address
        
        Returns:
            Merchant object
        """
        return self.create_merchant(
            db=db,
            merchant_name=f"{beneficiary_name}",
            wallet_address=beneficiary_wallet,
            merchant_type=MerchantType.FUNDRAISER,
            description=f"Fundraiser: {fund_title}",
            fund_id=fund_id
        )
    
    def deactivate_merchant(self, db: Session, merchant_id: str) -> bool:
        """Deactivate a merchant account"""
        merchant = self.get_merchant_by_id(db, merchant_id)
        if not merchant:
            return False
        
        merchant.is_active = False
        db.commit()
        logger.info(f"Deactivated merchant: {merchant_id}")
        return True


# Global service instance
merchant_service = MerchantService()
