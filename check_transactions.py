from backend.database import SessionLocal
from backend.models.transaction import Transaction

db = SessionLocal()
phone = "+918237987667"

try:
    # Get all transactions for this user
    txs = db.query(Transaction).filter(
        (Transaction.from_phone == phone) | (Transaction.to_phone == phone)
    ).order_by(Transaction.created_at.desc()).all()
    
    print(f"Total transactions: {len(txs)}\n")
    
    for tx in txs:
        print(f"ID: {tx.id}")
        print(f"From: {tx.from_phone}")
        print(f"To: {tx.to_phone}")
        print(f"Amount: {tx.amount} ALGO")
        print(f"Status: {tx.status}")
        print(f"Created: {tx.created_at}")
        if tx.tx_id:
            print(f"Blockchain TX: {tx.tx_id}")
        print("-" * 50)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
