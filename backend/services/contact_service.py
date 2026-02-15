"""
Contact Service - Manages name-to-phone contact mapping
Enables users to pay by name instead of phone number
"""
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import Optional, List, Dict, Tuple
import logging
import re

from backend.models.contact import Contact
from backend.models.user import User

logger = logging.getLogger(__name__)


class ContactService:
    """Service for managing user contacts and resolving names to phone numbers"""
    
    def save_contact(self, db: Session, owner_phone: str, nickname: str, contact_phone: str) -> Contact:
        """
        Save a contact with a nickname
        
        Args:
            db: Database session
            owner_phone: Phone number of the user saving the contact
            nickname: Name/nickname to save (will be lowercased)
            contact_phone: Phone number of the contact
            
        Returns:
            Contact object
        """
        nickname_lower = nickname.strip().lower()
        
        if not nickname_lower:
            raise ValueError("Contact name cannot be empty")
        
        if not re.match(r'^\+\d{10,15}$', contact_phone):
            raise ValueError("Invalid phone number format. Use +91XXXXXXXXXX")
        
        # Check if nickname already exists for this user - update if so
        existing = db.query(Contact).filter(
            Contact.owner_phone == owner_phone,
            Contact.nickname == nickname_lower
        ).first()
        
        if existing:
            existing.contact_phone = contact_phone
            db.commit()
            db.refresh(existing)
            logger.info(f"Updated contact: {owner_phone} -> {nickname_lower} = {contact_phone}")
            return existing
        
        # Create new contact
        contact = Contact(
            owner_phone=owner_phone,
            nickname=nickname_lower,
            contact_phone=contact_phone
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
        logger.info(f"Saved contact: {owner_phone} -> {nickname_lower} = {contact_phone}")
        return contact
    
    def remove_contact(self, db: Session, owner_phone: str, nickname: str) -> bool:
        """
        Remove a saved contact
        
        Returns:
            True if contact was removed, False if not found
        """
        nickname_lower = nickname.strip().lower()
        
        contact = db.query(Contact).filter(
            Contact.owner_phone == owner_phone,
            Contact.nickname == nickname_lower
        ).first()
        
        if not contact:
            return False
        
        db.delete(contact)
        db.commit()
        logger.info(f"Removed contact: {owner_phone} -> {nickname_lower}")
        return True
    
    def list_contacts(self, db: Session, owner_phone: str) -> List[Contact]:
        """Get all contacts for a user"""
        return db.query(Contact).filter(
            Contact.owner_phone == owner_phone
        ).order_by(Contact.nickname).all()
    
    def resolve_name(self, db: Session, owner_phone: str, name: str) -> Tuple[Optional[str], str]:
        """
        Resolve a name to a phone number
        
        Lookup order:
        1. User's saved contacts (exact match)
        2. Global user display names (exact match)
        3. Partial matches in contacts
        4. Partial matches in display names
        
        Args:
            db: Database session
            owner_phone: Phone number of the user doing the lookup
            name: Name to resolve
            
        Returns:
            Tuple of (phone_number, display_info) or (None, error_message)
        """
        name_lower = name.strip().lower()
        
        if not name_lower:
            return None, "Please provide a name to look up."
        
        # 1. Exact match in user's saved contacts
        try:
            contact = db.query(Contact).filter(
                Contact.owner_phone == owner_phone,
                Contact.nickname == name_lower
            ).first()
            
            if contact:
                return contact.contact_phone, f"📒 {contact.nickname} ({contact.contact_phone})"
        except Exception as e:
            logger.warning(f"Contact lookup failed: {e}")
            db.rollback()
        
        # 2. Exact match in global display names
        try:
            user = db.query(User).filter(
                sql_func.lower(User.display_name) == name_lower
            ).first()
            
            if user:
                return user.phone_number, f"👤 {user.display_name} ({user.phone_number})"
        except Exception as e:
            logger.warning(f"Display name lookup failed: {e}")
            db.rollback()
        
        # 3. Partial match in user's contacts
        try:
            partial_contacts = db.query(Contact).filter(
                Contact.owner_phone == owner_phone,
                Contact.nickname.ilike(f"%{name_lower}%")
            ).all()
            
            if len(partial_contacts) == 1:
                c = partial_contacts[0]
                return c.contact_phone, f"📒 {c.nickname} ({c.contact_phone})"
            
            if len(partial_contacts) > 1:
                matches = "\n".join([f"  • {c.nickname} → {c.contact_phone}" for c in partial_contacts])
                return None, f"Multiple contacts match *\"{name}\"*:\n{matches}\n\nPlease be more specific or use the full name."
        except Exception as e:
            logger.warning(f"Partial contact lookup failed: {e}")
            db.rollback()
        
        # 4. Partial match in global display names
        try:
            partial_users = db.query(User).filter(
                User.display_name.isnot(None),
                sql_func.lower(User.display_name).like(f"%{name_lower}%")
            ).all()
            
            if len(partial_users) == 1:
                u = partial_users[0]
                return u.phone_number, f"👤 {u.display_name} ({u.phone_number})"
            
            if len(partial_users) > 1:
                matches = "\n".join([f"  • {u.display_name} → {u.phone_number}" for u in partial_users])
                return None, f"Multiple users match *\"{name}\"*:\n{matches}\n\nPlease be more specific or use `save <name> as <phone>` to save a contact."
        except Exception as e:
            logger.warning(f"Partial display name lookup failed: {e}")
            db.rollback()
        
        # No match found
        return None, f"No contact found for *\"{name}\"*.\n\n💡 Save contacts with:\n`save {name} as +91XXXXXXXXXX`"
    
    def set_display_name(self, db: Session, phone: str, name: str) -> User:
        """
        Set a display name for a user so others can find them by name
        
        Args:
            db: Database session
            phone: User's phone number
            name: Display name to set
            
        Returns:
            Updated User object
        """
        user = db.query(User).filter(User.phone_number == phone).first()
        
        if not user:
            raise ValueError(f"User with phone {phone} not found")
        
        user.display_name = name.strip()
        db.commit()
        db.refresh(user)
        logger.info(f"Set display name for {phone}: {name}")
        return user


# Global instance
contact_service = ContactService()
