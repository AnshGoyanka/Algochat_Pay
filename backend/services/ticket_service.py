"""
Ticket service - NFT event tickets as Algorand ASAs
"""
from sqlalchemy.orm import Session
import logging
import secrets
from datetime import datetime
from backend.models.ticket import Ticket
from backend.algorand.client import algorand_client
from backend.services.wallet_service import wallet_service

logger = logging.getLogger(__name__)


class TicketService:
    """
    Manages event tickets as Algorand NFTs
    Each ticket is a unique ASA (Algorand Standard Asset)
    """
    
    def create_ticket(
        self,
        db: Session,
        event_name: str,
        buyer_phone: str,
        ticket_metadata: dict = None
    ) -> Ticket:
        """
        Create and mint a new event ticket NFT
        
        Args:
            db: Database session
            event_name: Name of the event
            buyer_phone: Buyer's phone number
            ticket_metadata: Optional metadata dict
        
        Returns:
            Ticket record
        """
        # Get or create buyer wallet
        buyer, _ = wallet_service.get_or_create_wallet(db, buyer_phone)
        
        # Generate unique ticket number
        ticket_number = self._generate_ticket_number(event_name)
        
        # Get buyer's private key for NFT creation
        buyer_private_key = wallet_service.get_private_key(db, buyer_phone)
        
        try:
            # Create NFT on Algorand
            asset_id = algorand_client.create_nft_asset(
                creator_private_key=buyer_private_key,
                asset_name=f"{event_name} Ticket",
                unit_name="TIX",
                total=1,  # Unique NFT
                metadata_url=f"https://algochat.app/tickets/{ticket_number}"
            )
            
            # Create ticket record
            ticket = Ticket(
                event_name=event_name,
                owner_phone=buyer_phone,
                owner_address=buyer.wallet_address,
                asset_id=asset_id,
                ticket_number=ticket_number,
                ticket_metadata=str(ticket_metadata) if ticket_metadata else None
            )
            
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            
            logger.info(f"Created ticket {ticket_number} for {event_name}")
            return ticket
            
        except Exception as e:
            logger.error(f"Ticket creation failed: {e}")
            raise
    
    def verify_ticket(self, db: Session, ticket_number: str) -> dict:
        """
        Verify ticket authenticity and validity
        
        Args:
            db: Database session
            ticket_number: Unique ticket identifier
        
        Returns:
            Dict with verification results
        """
        ticket = db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first()
        
        if not ticket:
            return {
                "valid": False,
                "reason": "Ticket not found",
                "ticket_number": ticket_number
            }
        
        if not ticket.is_valid:
            return {
                "valid": False,
                "reason": "Ticket has been invalidated",
                "ticket_number": ticket_number
            }
        
        if ticket.is_used:
            return {
                "valid": False,
                "reason": "Ticket already used",
                "ticket_number": ticket_number,
                "used_at": ticket.used_at.isoformat() if ticket.used_at else None
            }
        
        # Verify on-chain ownership
        assets = algorand_client.get_account_assets(ticket.owner_address)
        has_asset = any(asset.get("asset-id") == ticket.asset_id for asset in assets)
        
        if not has_asset:
            return {
                "valid": False,
                "reason": "NFT not found in owner's wallet",
                "ticket_number": ticket_number
            }
        
        return {
            "valid": True,
            "ticket_number": ticket_number,
            "event_name": ticket.event_name,
            "owner_phone": ticket.owner_phone,
            "asset_id": ticket.asset_id,
            "created_at": ticket.created_at.isoformat() if ticket.created_at else None
        }
    
    def mark_ticket_used(self, db: Session, ticket_number: str) -> Ticket:
        """
        Mark ticket as used (entry granted)
        
        Args:
            db: Database session
            ticket_number: Ticket identifier
        
        Returns:
            Updated Ticket record
        """
        ticket = db.query(Ticket).filter(Ticket.ticket_number == ticket_number).first()
        
        if not ticket:
            raise ValueError(f"Ticket not found: {ticket_number}")
        
        if ticket.is_used:
            raise ValueError(f"Ticket already used")
        
        ticket.is_used = True
        ticket.used_at = datetime.utcnow()
        
        db.commit()
        db.refresh(ticket)
        
        logger.info(f"Marked ticket {ticket_number} as used")
        return ticket
    
    def get_user_tickets(self, db: Session, phone_number: str) -> list[Ticket]:
        """
        Get all tickets owned by a user
        
        Args:
            db: Database session
            phone_number: User's phone number
        
        Returns:
            List of Ticket records
        """
        return db.query(Ticket).filter(Ticket.owner_phone == phone_number).all()
    
    def _generate_ticket_number(self, event_name: str) -> str:
        """Generate unique ticket number"""
        prefix = event_name[:3].upper()
        random_part = secrets.token_hex(6).upper()
        return f"{prefix}-{random_part}"


# Global service instance
ticket_service = TicketService()
