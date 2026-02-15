"""
Seed data for Events and Fundraising Campaigns
Run this script to populate the database with initial data
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import SessionLocal, init_db
from backend.models.event import Event
from backend.models.fund import Fund
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_events(db: Session):
    """Create 5 current active events from Luma"""
    
    events_data = [
        # Blockchain Conference - Major Event
        {
            "name": "Consensus Hong Kong 2026",
            "category": "technology",
            "description": "Asia's largest blockchain and Web3 conference. Join 5,000+ crypto leaders, builders, and investors. Featuring Vitalik Buterin, CZ, and top DeFi founders. Network with VCs and explore the future of decentralized finance.",
            "venue": "Hong Kong Convention Centre, Hong Kong",
            "event_date": datetime.utcnow() + timedelta(days=45),  # March 2026
            "ticket_price": 150.0,
            "total_capacity": 5000,
            "organizer": "CoinDesk",
            "image_url": "https://consensus.coindesk.com/hk-2026.jpg"
        },
        
        # Tech Startup Event - India
        {
            "name": "TechCrunch Startup Battlefield India",
            "category": "technology",
            "description": "Pitch competition for India's hottest startups. $100K prize pool. Meet investors from Sequoia, Accel, and Y Combinator. Demo day with live judging by tech industry legends.",
            "venue": "Bengaluru International Centre, Bengaluru",
            "event_date": datetime.utcnow() + timedelta(days=22),  # Early March 2026
            "ticket_price": 35.0,
            "total_capacity": 800,
            "organizer": "TechCrunch",
            "image_url": "https://techcrunch.com/events/india-battlefield.jpg"
        },
        
        # AI/ML Workshop
        {
            "name": "AI Builders Summit Mumbai",
            "category": "technology",
            "description": "Hands-on AI workshop series: Build ChatGPT clones, fine-tune LLMs, and deploy ML models. Speakers from OpenAI, Google DeepMind, and local AI startups. Includes certification.",
            "venue": "IIT Bombay Research Park, Mumbai",
            "event_date": datetime.utcnow() + timedelta(days=12),  # Late Feb 2026
            "ticket_price": 25.0,
            "total_capacity": 300,
            "organizer": "AI India Community",
            "image_url": "https://ai-builders.in/summit-2026.jpg"
        },
        
        # Music Festival
        {
            "name": "Sunburn Festival Goa 2026",
            "category": "music",
            "description": "Asia's biggest EDM festival returns! 3-day beach party with Martin Garrix, David Guetta, and KSHMR. Multiple stages, art installations, beach camping, and legendary afterparties.",
            "venue": "Vagator Beach, Goa",
            "event_date": datetime.utcnow() + timedelta(days=18),  # Early March 2026
            "ticket_price": 80.0,
            "total_capacity": 15000,
            "organizer": "Sunburn Events",
            "image_url": "https://sunburn.in/goa-2026-poster.jpg"
        },
        
        # Networking & Career
        {
            "name": "Product Management Bootcamp",
            "category": "education",
            "description": "2-day intensive PM bootcamp. Learn from ex-Google/Meta PMs. Master product strategy, roadmapping, and user research. Practice mock interviews. Network with 200+ aspiring PMs.",
            "venue": "91springboard, Hyderabad",
            "event_date": datetime.utcnow() + timedelta(days=8),  # Late Feb 2026
            "ticket_price": 18.0,
            "total_capacity": 200,
            "organizer": "Product School India",
            "image_url": "https://productschool.com/india-bootcamp.jpg"
        }
    ]
    
    created_count = 0
    for event_data in events_data:
        # Check if event already exists
        existing = db.query(Event).filter(Event.name == event_data["name"]).first()
        if not existing:
            event = Event(**event_data)
            db.add(event)
            created_count += 1
            logger.info(f"✅ Created event: {event_data['name']}")
        else:
            logger.info(f"⏭️  Event already exists: {event_data['name']}")
    
    db.commit()
    logger.info(f"\n🎫 Total events created: {created_count}/{len(events_data)}")


def seed_fundraisers(db: Session):
    """Create 5 current active fundraising campaigns"""
    
    fundraisers_data = [
        # Medical Emergency - URGENT
        {
            "creator_phone": "+919999999999",  # System account
            "title": "Heart Surgery for 8-Year-Old Girl",
            "description": "Meera needs urgent heart surgery. Her parents are daily wage workers who cannot afford the ₹12L medical cost. Every contribution saves a life. Hospital: Apollo Delhi. Surgery scheduled for March 5, 2026.",
            "goal_amount": 600.0,
            "deadline_hours": 168  # 7 days - URGENT
        },
        
        # Education Support
        {
            "creator_phone": "+919999999999",
            "title": "Laptops for 50 Rural Students",
            "description": "COVID forced schools online, but these village students (Grades 9-12) have no devices. Help them attend classes, do homework, and prepare for board exams. Partnered with Govt School, Bihar.",
            "goal_amount": 400.0,
            "deadline_hours": 480  # 20 days
        },
        
        # Disaster Relief
        {
            "creator_phone": "+919999999999",
            "title": "Earthquake Relief Uttarakhand",
            "description": "5.8 magnitude earthquake hit Uttarakhand yesterday. 200+ families homeless, no food/water. Funds buy tents, blankets, medicines, and meals. Verified NGO: Goonj Foundation. 100% transparent usage.",
            "goal_amount": 800.0,
            "deadline_hours": 120  # 5 days - URGENT
        },
        
        # Environmental Initiative
        {
            "creator_phone": "+919999999999",
            "title": "Save Mumbai's Mangroves",
            "description": "Developers want to cut 5000+ mangrove trees for construction. We're fighting legally to protect this coastal forest (prevents flooding, filters air). Funds cover court fees, awareness campaigns, and tree guardians.",
            "goal_amount": 350.0,
            "deadline_hours": 360  # 15 days
        },
        
        # Animal Welfare
        {
            "creator_phone": "+919999999999",
            "title": "Street Dog Vaccination Drive",
            "description": "Rabies outbreak in Pune area. Vaccinate 500 stray dogs to prevent spread. Includes sterilization to control population humanely. Partnered with Animal Welfare Board. Vet team ready to deploy.",
            "goal_amount": 250.0,
            "deadline_hours": 240  # 10 days
        }
    ]
    
    created_count = 0
    for fund_data in fundraisers_data:
        # Check if fund already exists
        existing = db.query(Fund).filter(Fund.title == fund_data["title"]).first()
        if not existing:
            deadline = datetime.utcnow() + timedelta(hours=fund_data.pop("deadline_hours"))
            fund = Fund(**fund_data, deadline=deadline)
            db.add(fund)
            created_count += 1
            logger.info(f"✅ Created fundraiser: {fund_data['title']}")
        else:
            logger.info(f"⏭️  Fundraiser already exists: {fund_data['title']}")
    
    db.commit()
    logger.info(f"\n💰 Total fundraisers created: {created_count}/{len(fundraisers_data)}")


def main():
    """Main seeding function"""
    logger.info("🌱 Starting database seeding...\n")
    
    # Initialize database (create tables if they don't exist)
    init_db()
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Seed events
        logger.info("📅 Seeding Events...")
        seed_events(db)
        
        logger.info("\n" + "="*60 + "\n")
        
        # Seed fundraisers
        logger.info("🎯 Seeding Fundraisers...")
        seed_fundraisers(db)
        
        logger.info("\n" + "="*60)
        logger.info("✅ Database seeding completed successfully!")
        logger.info("\nYou can now use these commands:")
        logger.info("  • list events - See all available events")
        logger.info("  • buy ticket TechFest 2026 - Purchase event ticket")
        logger.info("  • list funds - See active fundraisers")
        logger.info("  • contribute 50 ALGO to fund 1 - Donate to cause")
        
    except Exception as e:
        logger.error(f"❌ Seeding failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
