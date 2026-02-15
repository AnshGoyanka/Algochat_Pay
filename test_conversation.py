"""
Test conversational commitment creation
Simulates the guided conversation flow
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


def test_conversational_flow():
    """Test the full conversational commitment creation"""
    
    db = SessionLocal()
    test_phone = "whatsapp:+918237987667"
    
    try:
        print("=" * 60)
        print("CONVERSATIONAL COMMITMENT CREATION TEST")
        print("=" * 60)
        
        # Step 1: Trigger conversation with natural language
        print("\n📱 User: 'make a goa trip'")
        response = whatsapp_bot.process_message(db, test_phone, "make a goa trip")
        print(f"\n🤖 Bot:\n{response}")
        
        # Step 2: Provide amount
        print("\n" + "-" * 60)
        print("\n📱 User: '500'")
        response = whatsapp_bot.process_message(db, test_phone, "500")
        print(f"\n🤖 Bot:\n{response}")
        
        # Step 3: Provide participants
        print("\n" + "-" * 60)
        print("\n📱 User: '5 people'")
        response = whatsapp_bot.process_message(db, test_phone, "5 people")
        print(f"\n🤖 Bot:\n{response}")
        
        # Step 4: Provide deadline
        print("\n" + "-" * 60)
        print("\n📱 User: '7 days'")
        response = whatsapp_bot.process_message(db, test_phone, "7 days")
        print(f"\n🤖 Bot:\n{response}")
        
        # Step 5: Confirm
        print("\n" + "-" * 60)
        print("\n📱 User: 'yes'")
        response = whatsapp_bot.process_message(db, test_phone, "yes")
        print(f"\n🤖 Bot:\n{response}")
        
        print("\n" + "=" * 60)
        print("✅ CONVERSATIONAL FLOW TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_cancel_conversation():
    """Test cancelling mid-conversation"""
    
    db = SessionLocal()
    test_phone = "whatsapp:+919545296699"
    
    try:
        print("\n\n" + "=" * 60)
        print("CANCEL CONVERSATION TEST")
        print("=" * 60)
        
        # Start conversation
        print("\n📱 User: 'create Kokan Trip'")
        response = whatsapp_bot.process_message(db, test_phone, "create Kokan Trip")
        print(f"\n🤖 Bot:\n{response}")
        
        # Provide amount
        print("\n" + "-" * 60)
        print("\n📱 User: '1000'")
        response = whatsapp_bot.process_message(db, test_phone, "1000")
        print(f"\n🤖 Bot:\n{response}")
        
        # Cancel mid-way
        print("\n" + "-" * 60)
        print("\n📱 User: 'cancel'")
        response = whatsapp_bot.process_message(db, test_phone, "cancel")
        print(f"\n🤖 Bot:\n{response}")
        
        # Try sending another message (should not be in conversation)
        print("\n" + "-" * 60)
        print("\n📱 User: '5' (should not be processed as participant count)")
        response = whatsapp_bot.process_message(db, test_phone, "5")
        print(f"\n🤖 Bot:\n{response}")
        
        print("\n" + "=" * 60)
        print("✅ CANCEL TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def test_trigger_patterns():
    """Test various trigger patterns"""
    
    db = SessionLocal()
    test_phone = "whatsapp:+918237987667"
    
    try:
        print("\n\n" + "=" * 60)
        print("TRIGGER PATTERN TEST")
        print("=" * 60)
        
        test_messages = [
            "make a goa trip",
            "make goa trip",
            "create birthday party",
            "new commitment for weekend getaway",
            "start lock for hackathon"
        ]
        
        for msg in test_messages:
            print(f"\n📱 Testing: '{msg}'")
            trigger = whatsapp_bot._detect_conversation_trigger(msg)
            print(f"   Extracted title: {trigger}")
            
            # Clear any state
            from bot.conversation_state import conversation_manager
            conversation_manager.clear_state(test_phone.replace("whatsapp:", ""))
        
        print("\n" + "=" * 60)
        print("✅ TRIGGER PATTERN TEST COMPLETE")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    # Test trigger patterns first
    test_trigger_patterns()
    
    # Test full conversational flow
    test_conversational_flow()
    
    # Test cancellation
    test_cancel_conversation()
