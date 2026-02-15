"""
Test improved quick add with database fallback
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.whatsapp_webhook import whatsapp_bot
from bot.conversation_state import conversation_manager
from backend.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_add_with_expired_context():
    """Test adding participant when context expired but commitment exists in DB"""
    
    db = SessionLocal()
    organizer_phone = "whatsapp:+918237987667"
    
    try:
        print("=" * 60)
        print("TEST: ADD WITH EXPIRED CONTEXT (DATABASE FALLBACK)")
        print("=" * 60)
        
        # Clear any existing context (simulate expired)
        phone_clean = organizer_phone.replace("whatsapp:", "")
        conversation_manager.clear_context(phone_clean)
        print("\n✓ Cleared context (simulating expiration)")
        
        # Now try to add participant - should find commitment #4 from database
        print("\n📱 User: 'add +919545296699' (context expired, but commitment #4 exists in DB)")
        response = whatsapp_bot.process_message(db, organizer_phone, "add +919545296699")
        print(f"\n🤖 Bot:\n{response}")
        
        print("\n" + "=" * 60)
        print("✅ DATABASE FALLBACK TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_add_with_no_commitments():
    """Test adding when user has no commitments at all"""
    
    db = SessionLocal()
    test_phone = "whatsapp:+910000000001"  # User with no commitments
    
    try:
        print("\n\n" + "=" * 60)
        print("TEST: ADD WITH NO COMMITMENTS (IMPROVED ERROR)")
        print("=" * 60)
        
        print("\n📱 User: 'add +919545296699' (no commitments exist)")
        response = whatsapp_bot.process_message(db, test_phone, "add +919545296699")
        print(f"\n🤖 Bot:\n{response}")
        
        print("\n" + "=" * 60)
        print("✅ NO COMMITMENTS ERROR MESSAGE TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_add_after_create():
    """Test the full flow: create then add immediately"""
    
    db = SessionLocal()
    organizer_phone = "whatsapp:+918237987667"
    
    try:
        print("\n\n" + "=" * 60)
        print("TEST: CREATE THEN ADD (NORMAL FLOW)")
        print("=" * 60)
        
        # Create commitment
        print("\n📱 User: 'make a weekend trip'")
        response = whatsapp_bot.process_message(db, organizer_phone, "make a weekend trip")
        print(f"\n🤖 Bot:\n{response[:100]}...")
        
        # Complete conversation quickly
        whatsapp_bot.process_message(db, organizer_phone, "200")
        whatsapp_bot.process_message(db, organizer_phone, "4")
        whatsapp_bot.process_message(db, organizer_phone, "3")
        response = whatsapp_bot.process_message(db, organizer_phone, "yes")
        print(f"\n🤖 Bot (after 'yes'):\n{response}")
        
        # Now add participant immediately (context should exist)
        print("\n" + "-" * 60)
        print("\n📱 User: 'add +919545296699'")
        response = whatsapp_bot.process_message(db, organizer_phone, "add +919545296699")
        print(f"\n🤖 Bot:\n{response}")
        
        print("\n" + "=" * 60)
        print("✅ NORMAL FLOW TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # Test 1: Normal flow (create then add)
    test_add_after_create()
    
    # Test 2: Add with expired context but commitment exists
    test_add_with_expired_context()
    
    # Test 3: Add with no commitments (improved error message)
    test_add_with_no_commitments()
