"""
Test the funds command to see how it displays
"""
from backend.database import SessionLocal
from bot.whatsapp_webhook import whatsapp_bot

db = SessionLocal()
phone = "+918237987667"

try:
    # Test funds command
    response = whatsapp_bot.process_message(db, f"whatsapp:{phone}", "funds")
    print("=" * 60)
    print("FUNDS COMMAND RESPONSE:")
    print("=" * 60)
    print(response)
    print("=" * 60)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
