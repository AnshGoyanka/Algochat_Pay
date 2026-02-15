"""
Conversation State Manager - Track multi-step conversations
For guided commitment creation and other multi-step flows
"""
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ConversationState:
    """
    Stores conversation state for a user
    """
    def __init__(self, flow_type: str):
        self.flow_type = flow_type  # "create_commitment", etc.
        self.step = 0
        self.data = {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def next_step(self):
        """Move to next step"""
        self.step += 1
        self.updated_at = datetime.utcnow()
    
    def set_data(self, key: str, value):
        """Store data for this conversation"""
        self.data[key] = value
        self.updated_at = datetime.utcnow()
    
    def get_data(self, key: str, default=None):
        """Retrieve data"""
        return self.data.get(key, default)
    
    def is_expired(self, minutes=60):
        """Check if conversation expired (default 60 minutes)"""
        age = datetime.utcnow() - self.updated_at
        return age > timedelta(minutes=minutes)


class ConversationStateManager:
    """
    Manages conversation states for all users
    In-memory storage (for production, use Redis)
    """
    
    def __init__(self):
        self.states: Dict[str, ConversationState] = {}  # phone -> ConversationState
        self.context: Dict[str, Dict] = {}  # phone -> context data (last_commitment_id, etc.)
    
    def create_state(self, phone: str, flow_type: str) -> ConversationState:
        """Start a new conversation flow"""
        state = ConversationState(flow_type)
        self.states[phone] = state
        logger.info(f"Started {flow_type} conversation for {phone}")
        return state
    
    def get_state(self, phone: str) -> Optional[ConversationState]:
        """Get current conversation state"""
        state = self.states.get(phone)
        
        # Clean up expired states
        if state and state.is_expired():
            del self.states[phone]
            logger.info(f"Expired conversation state for {phone}")
            return None
        
        return state
    
    def clear_state(self, phone: str):
        """Clear conversation state (conversation completed or cancelled)"""
        if phone in self.states:
            del self.states[phone]
            logger.info(f"Cleared conversation state for {phone}")
    
    def has_active_conversation(self, phone: str) -> bool:
        """Check if user has active conversation"""
        state = self.get_state(phone)
        return state is not None
    
    def cleanup_old_states(self):
        """Remove all expired states (call periodically)"""
        expired = [
            phone for phone, state in self.states.items()
            if state.is_expired()
        ]
        for phone in expired:
            del self.states[phone]
        if expired:
            logger.info(f"Cleaned up {len(expired)} expired conversation states")
    
    # ===== Context Management =====
    
    def set_context(self, phone: str, key: str, value):
        """Store context data (e.g., last_commitment_id)"""
        if phone not in self.context:
            self.context[phone] = {}
        self.context[phone][key] = value
        logger.info(f"Set context for {phone}: {key}={value}")
    
    def get_context(self, phone: str, key: str, default=None):
        """Retrieve context data"""
        return self.context.get(phone, {}).get(key, default)
    
    def clear_context(self, phone: str, key: str = None):
        """Clear specific context key or all context for user"""
        if key:
            if phone in self.context:
                self.context[phone].pop(key, None)
                logger.info(f"Cleared context {key} for {phone}")
        else:
            if phone in self.context:
                del self.context[phone]
                logger.info(f"Cleared all context for {phone}")


# Global singleton
conversation_manager = ConversationStateManager()
