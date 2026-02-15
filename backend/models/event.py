"""
Event model - Available events for ticket purchase
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.sql import func
from datetime import datetime
from backend.database import Base


class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, unique=True)
    category = Column(String(50), nullable=False)  # tech, music, sports, education
    description = Column(String(1000))
    venue = Column(String(200))
    event_date = Column(DateTime(timezone=True))
    ticket_price = Column(Float, nullable=False)  # Price in ALGO
    total_capacity = Column(Integer, default=100)
    tickets_sold = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    image_url = Column(String(500))
    organizer = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    @property
    def tickets_available(self):
        """Calculate remaining tickets"""
        return self.total_capacity - self.tickets_sold
    
    @property
    def is_sold_out(self):
        """Check if event is sold out"""
        return self.tickets_sold >= self.total_capacity
    
    @property
    def is_upcoming(self):
        """Check if event is in the future"""
        if not self.event_date:
            return True
        return self.event_date > datetime.utcnow()
    
    def __repr__(self):
        return f"<Event {self.name} - {self.ticket_price} ALGO>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "venue": self.venue,
            "event_date": self.event_date.isoformat() if self.event_date else None,
            "ticket_price": self.ticket_price,
            "tickets_available": self.tickets_available,
            "is_sold_out": self.is_sold_out,
            "organizer": self.organizer
        }
