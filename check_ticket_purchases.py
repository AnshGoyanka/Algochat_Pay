"""
Check transactions to find which events were actually purchased
"""
from backend.database import SessionLocal
from backend.models.transaction import Transaction
from backend.models.ticket import Ticket

db = SessionLocal()
phone = "+918237987667"

try:
    # Get all transactions for this user
    from backend.models.transaction import TransactionType
    
    txs = db.query(Transaction).filter(
        Transaction.sender_phone == phone,
        Transaction.transaction_type == TransactionType.TICKET
    ).order_by(Transaction.timestamp.asc()).all()
    
    print(f"Ticket Purchase Transactions: {len(txs)}\n")
    
    for tx in txs:
        print(f"Transaction ID: {tx.id}")
        print(f"Type: {tx.transaction_type}")
        print(f"Amount: {tx.amount} ALGO")
        print(f"Note: {tx.note}")
        print(f"Created: {tx.timestamp}")
        print(f"TX ID: {tx.tx_id}")
        print("-" * 50)
    
    # Also check tickets
    print("\n\nCurrent Tickets:")
    tickets = db.query(Ticket).filter(Ticket.owner_phone == phone).all()
    for ticket in tickets:
        print(f"Ticket: {ticket.ticket_number}")
        print(f"  Event: '{ticket.event_name}'")
        print(f"  Asset ID: {ticket.asset_id}")
        print(f"  Created: {ticket.created_at}")
        print()
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
