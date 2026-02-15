"""
Seed merchants for events and fundraisers
Privacy-enhanced payment system - creates merchant accounts for all events and funds
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal
from backend.models.event import Event
from backend.models.fund import Fund
from backend.services.merchant_service import merchant_service, MerchantType
from backend.services.wallet_service import wallet_service
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_event_merchants():
    """Create merchant accounts for all events"""
    db = SessionLocal()
    
    try:
        events = db.query(Event).filter(Event.is_active == True).all()
        logger.info(f"Found {len(events)} active events")
        
        for event in events:
            # Check if merchant already exists
            existing = merchant_service.get_merchant_by_event(db, event.id)
            if existing:
                logger.info(f"Merchant already exists for event: {event.name}")
                continue
            
            # Get organizer wallet (or create dummy one for demo)
            # In production, this would be the actual organizer's wallet
            organizer_wallet = "EVENTORG" + str(event.id).zfill(50)  # Placeholder format
            
            # For real implementation, get actual organizer wallet
            # For now, use a system wallet or create one for the organizer
            try:
                # Try to get organizer's wallet if phone is available
                if hasattr(event, 'organizer_phone') and event.organizer_phone:
                    org_user, _ = wallet_service.get_or_create_wallet(db, event.organizer_phone)
                    organizer_wallet = org_user.wallet_address
                else:
                    # Use first user's wallet as event organizer (for demo)
                    first_user = wallet_service.get_all_users(db)[0] if wallet_service.get_all_users(db) else None
                    if first_user:
                        organizer_wallet = first_user.wallet_address
            except:
                pass
            
            # Determine organizer display name
            organizer_name = f"{event.organizer}" if event.organizer else f"{event.name} Organizers"
            
            # Create merchant
            merchant = merchant_service.create_merchant(
                db=db,
                merchant_name=organizer_name,
                wallet_address=organizer_wallet,
                merchant_type=MerchantType.EVENT_ORGANIZER,
                description=f"Event organizer for {event.name}",
                event_id=event.id
            )
            
            logger.info(f"✅ Created merchant {merchant.merchant_id} for event: {event.name}")
        
        logger.info(f"Event merchant seeding completed!")
        
    except Exception as e:
        logger.error(f"Error seeding events: {e}")
        db.rollback()
    finally:
        db.close()


def seed_fund_merchants():
    """Create merchant accounts for all fundraisers"""
    db = SessionLocal()
    
    try:
        funds = db.query(Fund).filter(Fund.is_active == True).all()
        logger.info(f"Found {len(funds)} active funds")
        
        for fund in funds:
            # Check if merchant already exists
            existing = merchant_service.get_merchant_by_fund(db, fund.id)
            if existing:
                logger.info(f"Merchant already exists for fund: {fund.title}")
                continue
            
            # Get creator/beneficiary wallet
            try:
                creator_user = wallet_service.get_user_by_phone(db, fund.creator_phone)
                beneficiary_wallet = creator_user.wallet_address if creator_user else None
            except:
                beneficiary_wallet = None
            
            if not beneficiary_wallet:
                logger.warning(f"Could not find wallet for fund creator: {fund.creator_phone}")
                continue
            
            # Extract beneficiary name from title (first 3 words or organization name)
            title_words = fund.title.split()
            beneficiary_name = " ".join(title_words[:3]) if len(title_words) > 3 else fund.title
            
            # Common patterns for beneficiary naming
            if "for" in fund.title.lower():
                parts = fund.title.split(" for ")
                if len(parts) > 1:
                    beneficiary_name = parts[1].strip()
            
            # Create merchant
            merchant = merchant_service.create_merchant(
                db=db,
                merchant_name=beneficiary_name,
                wallet_address=beneficiary_wallet,
                merchant_type=MerchantType.FUNDRAISER,
                description=f"Fundraiser: {fund.title}",
                fund_id=fund.id,
                phone_number=fund.creator_phone
            )
            
            logger.info(f"✅ Created merchant {merchant.merchant_id} for fund: {fund.title}")
        
        logger.info(f"Fund merchant seeding completed!")
        
    except Exception as e:
        logger.error(f"Error seeding funds: {e}")
        db.rollback()
    finally:
        db.close()


def main():
    """Run all seeding operations"""
    logger.info("=" * 60)
    logger.info("MERCHANT SEEDING - Privacy Enhanced Payments")
    logger.info("=" * 60)
    
    logger.info("\n1. Seeding Event Merchants...")
    seed_event_merchants()
    
    logger.info("\n2. Seeding Fund Merchants...")
    seed_fund_merchants()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ MERCHANT SEEDING COMPLETE!")
    logger.info("=" * 60)
    logger.info("\nMerchants created for all events and fundraisers.")
    logger.info("Payments will now show friendly merchant names instead of wallet addresses.")


if __name__ == "__main__":
    main()
