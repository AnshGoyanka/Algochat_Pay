"""
Assign each ticket to a different event based on purchase order
"""
from backend.database import SessionLocal
from backend.models.ticket import Ticket
from backend.models.event import Event

db = SessionLocal()
phone = "+918237987667"

try:
    # Get all tickets for this user, ordered by creation time
    tickets = db.query(Ticket).filter(
        Ticket.owner_phone == phone
    ).order_by(Ticket.created_at.asc()).all()
    
    # Get available events
    events = db.query(Event).filter(
        Event.is_active == True
    ).order_by(Event.event_date.asc()).all()
    
    print(f"Found {len(tickets)} tickets")
    print(f"Found {len(events)} active events\n")
    
    if len(tickets) <= len(events):
        # Assign each ticket to a different event
        for i, ticket in enumerate(tickets):
            old_event = ticket.event_name
            new_event = events[i].name
            ticket.event_name = new_event
            
            print(f"Ticket {ticket.ticket_number}:")
            print(f"  '{old_event}' → '{new_event}'")
            print(f"  Created: {ticket.created_at}")
            print()
        
        db.commit()
        print(f"✅ Updated {len(tickets)} tickets with unique event names")
    else:
        print("⚠️ More tickets than events!")
        
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
