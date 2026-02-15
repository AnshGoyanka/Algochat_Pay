"""
Clear old fundraisers and reseed with new 5 curated campaigns
"""
from backend.database import SessionLocal
from backend.models.fund import Fund
from scripts.seed_events_funds import seed_fundraisers
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    db = SessionLocal()
    try:
        # Delete all old fundraisers
        old_count = db.query(Fund).count()
        db.query(Fund).delete()
        db.commit()
        logger.info(f"🗑️  Deleted {old_count} old fundraisers")
        
        # Seed new fundraisers
        logger.info("🌱 Seeding new fundraisers...")
        seed_fundraisers(db)
        
        # Verify
        new_count = db.query(Fund).count()
        logger.info(f"\n✅ Database now has {new_count} fundraisers")
        
        # List them
        funds = db.query(Fund).order_by(Fund.deadline.asc()).all()
        print("\n💰 Current Fundraisers:\n")
        for i, fund in enumerate(funds, 1):
            days_left = (fund.deadline - fund.created_at).days if fund.deadline and fund.created_at else 0
            progress = (fund.current_amount / fund.goal_amount * 100) if fund.goal_amount > 0 else 0
            
            print(f"{i}. {fund.title}")
            print(f"   🎯 Goal: {fund.goal_amount} ALGO")
            print(f"   📊 Raised: {fund.current_amount} ALGO ({progress:.1f}%)")
            print(f"   ⏰ {days_left} days left")
            print()
            
    except Exception as e:
        logger.error(f"Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
