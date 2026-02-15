"""
Test quick add participant feature
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot.whatsapp_webhook import whatsapp_bot
from backend.database import SessionLocal
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_quick_add_participant():
    """Test adding participant with just 'add +91XXXXXXXXXX'"""
    
    db = SessionLocal()
    organizer_phone = "whatsapp:+918237987667"
    participant_phone = "+919545296699"
    
    try:
        print("=" * 60)
        print("QUICK ADD PARTICIPANT TEST")
        print("=" * 60)
        
        # Step 1: Create a commitment first
        print("\n📱 Organizer: 'make a test trip'")
        response = whatsapp_bot.process_message(db, organizer_phone, "make a test trip")
        print(f"\n🤖 Bot:\n{response}")
        
        # Step 2: Complete conversation
        print("\n" + "-" * 60)
        print("\n📱 Organizer: '100'")
        response = whatsapp_bot.process_message(db, organizer_phone, "100")
        print(f"\n🤖 Bot:\n{response}")
        
        print("\n" + "-" * 60)
        print("\n📱 Organizer: '3'")
        response = whatsapp_bot.process_message(db, organizer_phone, "3")
        print(f"\n🤖 Bot:\n{response}")
        
        print("\n" + "-" * 60)
        print("\n📱 Organizer: '5'")
        response = whatsapp_bot.process_message(db, organizer_phone, "5")
        print(f"\n🤖 Bot:\n{response}")
        
        print("\n" + "-" * 60)
        print("\n📱 Organizer: 'yes'")
        response = whatsapp_bot.process_message(db, organizer_phone, "yes")
        print(f"\n🤖 Bot:\n{response}")
        
        # Step 3: Now test quick add (the feature we're testing!)
        print("\n" + "=" * 60)
        print("NOW TESTING QUICK ADD FEATURE")
        print("=" * 60)
        
        print("\n📱 Organizer: 'add +919545296699'")
        response = whatsapp_bot.process_message(db, organizer_phone, "add +919545296699")
        print(f"\n🤖 Bot:\n{response}")
        
        # Step 4: Try adding another number with different format
        print("\n" + "-" * 60)
        print("\n📱 Organizer: 'add 918000000000' (without +)")
        response = whatsapp_bot.process_message(db, organizer_phone, "add 918000000000")
        print(f"\n🤖 Bot:\n{response}")
        
        print("\n" + "=" * 60)
        print("✅ QUICK ADD PARTICIPANT TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_add_without_context():
    """Test adding participant when no recent commitment exists"""
    
    db = SessionLocal()
    test_phone = "whatsapp:+910000000000"  # User with no recent commitment
    
    try:
        print("\n\n" + "=" * 60)
        print("ADD WITHOUT CONTEXT TEST")
        print("=" * 60)
        
        print("\n📱 User: 'add +919545296699' (no recent commitment)")
        response = whatsapp_bot.process_message(db, test_phone, "add +919545296699")
        print(f"\n🤖 Bot:\n{response}")
        
        print("\n" + "=" * 60)
        print("✅ NO CONTEXT TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_trigger_detection():
    """Test various add participant trigger patterns"""
    
    print("\n\n" + "=" * 60)
    print("ADD PARTICIPANT TRIGGER DETECTION TEST")
    print("=" * 60)
    
    test_messages = [
        "add +918237987667",
        "add 918237987667",
        "add 8237987667",
        "Add +919545296699",
        "ADD +918000000000",
        "hello",  # Should not match
        "add",  # Should not match (no number)
    ]
    
    for msg in test_messages:
        print(f"\n📱 Testing: '{msg}'")
        detected = whatsapp_bot._detect_add_participant(msg)
        print(f"   Extracted phone: {detected if detected else 'None (not detected)'}")
    
    print("\n" + "=" * 60)
    print("✅ TRIGGER DETECTION TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    # Test trigger detection first
    test_trigger_detection()
    
    # Test full quick add flow
    test_quick_add_participant()
    
    # Test adding without context
    test_add_without_context()
