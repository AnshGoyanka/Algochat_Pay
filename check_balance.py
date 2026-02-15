from backend.database import SessionLocal
from backend.services.wallet_service import wallet_service

db = SessionLocal()
phone = "+918237987667"

try:
    info = wallet_service.get_wallet_info(db, phone)
    print(f"Phone: {info['phone']}")
    print(f"Address: {info['address']}")
    print(f"Balance: {info['balance']} ALGO")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
