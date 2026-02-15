"""
Clear old events and reseed with new 5 curated events
"""
from backend.database import SessionLocal
from backend.models.event import Event
from scripts.seed_events_funds import seed_events
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = SessionLocal()
    try:
        # Delete all old events
        old_count = db.query(Event).count()
        db.query(Event).delete()
        db.commit()
        logger.info(f"🗑️  Deleted {old_count} old events")
        
        # Seed new events
        logger.info("🌱 Seeding new events...")
        seed_events(db)
        
        # Verify
        new_count = db.query(Event).count()
        logger.info(f"\n✅ Database now has {new_count} events")
        
        # List them
        events = db.query(Event).order_by(Event.event_date.asc()).all()
        print("\n📅 Current Events:\n")
        for i, event in enumerate(events, 1):
            print(f"{i}. {event.name}")
            print(f"   📍 {event.venue}")
            print(f"   📅 {event.event_date.strftime('%d %b %Y')}")
            print(f"   💎 {event.ticket_price} ALGO")
            print()
            
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
