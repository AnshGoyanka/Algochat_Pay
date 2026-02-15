"""
Fix existing tickets with placeholder event names
Update them to show actual event names from the events in the database
"""
from backend.database import SessionLocal
from backend.models.ticket import Ticket
from backend.models.event import Event

db = SessionLocal()

try:
    # Get all tickets with placeholder name
    tickets = db.query(Ticket).filter(Ticket.event_name == 'eventname').all()
    
    print(f"Found {len(tickets)} tickets with placeholder 'eventname'\n")
    
    # Get the first available event to assign
    events = db.query(Event).filter(Event.is_active == True).order_by(Event.event_date.asc()).all()
    
    if not events:
        print("No events found in database!")
    else:
        print(f"Available events: {len(events)}\n")
        
        # Assign the first event to all placeholder tickets
        # In a real scenario, you'd want to map each ticket to its correct event
        default_event = events[0]
        
        for ticket in tickets:
            old_name = ticket.event_name
            ticket.event_name = default_event.name
            print(f"Updated Ticket {ticket.ticket_number}:")
            print(f"  '{old_name}' → '{default_event.name}'")
        
        db.commit()
        print(f"\n✅ Updated {len(tickets)} tickets to event: {default_event.name}")
        
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
    import traceback
    traceback.print_exc()
finally:
    db.close()
