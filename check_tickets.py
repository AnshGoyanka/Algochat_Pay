"""
Check the actual tickets in the database for the user
"""
from backend.database import SessionLocal
from backend.models.ticket import Ticket

db = SessionLocal()
phone = "+918237987667"

try:
    tickets = db.query(Ticket).filter(Ticket.owner_phone == phone).all()
    
    print(f"Total tickets: {len(tickets)}\n")
    
    for ticket in tickets:
        print(f"Ticket ID: {ticket.id}")
        print(f"Event Name: '{ticket.event_name}'")
        print(f"Ticket Number: {ticket.ticket_number}")
        print(f"Asset ID: {ticket.asset_id}")
        print(f"Status - Valid: {ticket.is_valid}, Used: {ticket.is_used}")
        print("-" * 50)
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
