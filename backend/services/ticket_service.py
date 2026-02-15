"""
Ticket service - NFT event tickets as Algorand ASAs
"""
from sqlalchemy.orm import Session
import logging
import secrets
from datetime import datetime
from backend.models.ticket import Ticket
from backend.models.event import Event
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
            nft_result = algorand_client.create_nft_asset(
                creator_private_key=buyer_private_key,
                asset_name=f"{event_name} Ticket",
                unit_name="TIX",
                total=1,  # Unique NFT
                metadata_url=f"https://algochat.app/tickets/{ticket_number}"
            )
            
            asset_id = nft_result["asset_id"]
            tx_id = nft_result["tx_id"]
            
            # Create ticket record
            ticket = Ticket(
                event_name=event_name,
                owner_phone=buyer_phone,
                owner_address=buyer.wallet_address,
                asset_id=asset_id,
                tx_id=tx_id,
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
    
    def list_events(self, db: Session, category: str = None) -> list[Event]:
        """
        List available events (limited to 5 active events)
        
        Args:
            db: Database session
            category: Optional category filter
        
        Returns:
            List of active Event records (max 5)
        """
        query = db.query(Event).filter(Event.is_active == True)
        
        if category:
            query = query.filter(Event.category == category)
        
        # Limit to 5 events, sorted by date
        return query.order_by(Event.event_date.asc()).limit(5).all()
    
    def get_event_by_id(self, db: Session, event_id: int) -> Event:
        """
        Get event by ID
        
        Args:
            db: Database session
            event_id: Event ID
        
        Returns:
            Event record or None
        """
        return db.query(Event).filter(
            Event.id == event_id,
            Event.is_active == True
        ).first()
    
    def get_event_by_name(self, db: Session, event_name: str) -> Event:
        """
        Get event by exact or partial name match
        
        Args:
            db: Database session
            event_name: Event name (case insensitive)
        
        Returns:
            Event record or None
        """
        # Try exact match first
        event = db.query(Event).filter(
            Event.name.ilike(event_name),
            Event.is_active == True
        ).first()
        
        if event:
            return event
        
        # Try partial match
        event = db.query(Event).filter(
            Event.name.ilike(f"%{event_name}%"),
            Event.is_active == True
        ).first()
        
        return event
    
    def purchase_ticket(
        self,
        db: Session,
        buyer_phone: str,
        event_name: str = None,
        event_id: int = None
    ) -> dict:
        """
        Purchase ticket for an event (integrates with Event model)
        
        Args:
            db: Database session
            buyer_phone: Buyer's phone number
            event_name: Event name (optional)
            event_id: Event ID (optional)
        
        Returns:
            Dict with ticket details and event info
        """
        # Get event by ID or name
        if event_id:
            event = self.get_event_by_id(db, event_id)
            if not event:
                raise ValueError(f"Event not found with ID: {event_id}")
        elif event_name:
            event = self.get_event_by_name(db, event_name)
            if not event:
                raise ValueError(f"Event not found: {event_name}")
        else:
            raise ValueError("Either event_name or event_id must be provided")
        
        # Check availability
        if event.is_sold_out:
            raise ValueError(f"{event.name} is sold out!")
        
        # Get buyer wallet
        buyer, _ = wallet_service.get_or_create_wallet(db, buyer_phone)
        
        # Check buyer balance
        buyer_balance = algorand_client.get_balance(buyer.wallet_address)
        if buyer_balance < event.ticket_price + 0.001:
            raise ValueError(f"Insufficient balance. Need {event.ticket_price} ALGO + fees")
        
        # Get buyer's private key
        buyer_private_key = wallet_service.get_private_key(db, buyer_phone)
        
        try:
            # Create ticket metadata
            ticket_metadata = {
                "event_name": event.name,
                "venue": event.venue,
                "date": event.event_date.isoformat() if event.event_date else None,
                "price": event.ticket_price,
                "category": event.category
            }
            
            # Create ticket NFT
            ticket = self.create_ticket(
                db=db,
                event_name=event.name,
                buyer_phone=buyer_phone,
                ticket_metadata=ticket_metadata
            )
            
            # Increment tickets sold
            event.tickets_sold += 1
            db.commit()
            
            logger.info(f"Ticket purchased: {event.name} by {buyer_phone}")
            
            return {
                "success": True,
                "ticket_number": ticket.ticket_number,
                "event_name": event.name,
                "venue": event.venue,
                "event_date": event.event_date.isoformat() if event.event_date else None,
                "ticket_price": event.ticket_price,
                "asset_id": ticket.asset_id,
                "tx_id": ticket.tx_id,
                "remaining_tickets": event.tickets_available
            }
            
        except Exception as e:
            logger.error(f"Ticket purchase failed: {e}")
            raise


# Global service instance
ticket_service = TicketService()
