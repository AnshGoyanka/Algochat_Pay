"""
Natural Language Command Mapper
Maps conversational text to structured bot commands using regex patterns
"""

import re
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class ParsedCommand:
    """Represents a parsed natural language command"""
    command: str  # The command type (BALANCE, PAY, etc.)
    params: Dict[str, Any]  # Extracted parameters
    confidence: float  # Matching confidence (0.0 to 1.0)
    original_text: str


class NaturalLanguageMapper:
    """Maps natural language text to bot commands using pattern matching"""
    
    def __init__(self):
        # Command patterns: (regex_pattern, command_type, param_extractors)
        self.patterns = [
            # MENU command patterns
            (
                r'\b(?:show|display|get)\s+(?:the\s+)?menu\b',
                'MENU',
                {},
                1.0
            ),
            (
                r'\bmenu\b',
                'MENU',
                {},
                0.9
            ),
            (
                r'\bquick\s+(?:commands?|actions?)\b',
                'MENU',
                {},
                0.95
            ),
            
            # BALANCE command patterns
            (
                r'\b(?:show|check|what\'?s|display|get)\s+(?:me\s+)?(?:my\s+)?balance\b',
                'BALANCE',
                {},
                1.0
            ),
            (
                r'\bbalance\s+(?:check|inquiry|status)\b',
                'BALANCE',
                {},
                0.9
            ),
            (
                r'\bhow\s+much\s+(?:money|algo|algos?)\s+(?:do\s+i\s+have|have\s+i\s+got)\b',
                'BALANCE',
                {},
                0.95
            ),
            
            # HISTORY command patterns
            (
                r'\b(?:show|display|get|list)\s+(?:me\s+)?(?:my\s+)?(?:transaction\s+)?history\b',
                'HISTORY',
                {},
                1.0
            ),
            (
                r'\b(?:recent|past|previous)\s+transactions?\b',
                'HISTORY',
                {},
                0.95
            ),
            (
                r'\bwhat\s+(?:have\s+i\s+)?(?:sent|received|paid|spent)\b',
                'HISTORY',
                {},
                0.85
            ),
            
            # PAY command patterns
            (
                r'\b(?:send|pay|transfer)\s+(\d+(?:\.\d+)?)\s+(?:algo|algos?)\s+to\s+([\+\d\s\-\(\)]+)',
                'PAY',
                {'amount': 1, 'phone': 2},
                1.0
            ),
            (
                r'\bpay\s+([\+\d\s\-\(\)]+)\s+(\d+(?:\.\d+)?)\s+(?:algo|algos?)\b',
                'PAY',
                {'phone': 1, 'amount': 2},
                0.95
            ),
            (
                r'\btransfer\s+(\d+(?:\.\d+)?)\s+to\s+([\+\d\s\-\(\)]+)',
                'PAY',
                {'amount': 1, 'phone': 2},
                0.9
            ),
            
            # EVENTS command patterns
            (
                r'\b(?:show|list|display|get|what|see)\s+(?:me\s+)?(?:all\s+)?(?:available\s+)?events?\b',
                'EVENTS',
                {},
                1.0
            ),
            (
                r'\bevents?\s+(?:list|available)\b',
                'EVENTS',
                {},
                0.95
            ),
            (
                r'\bwhat\s+events?\s+(?:are\s+)?(?:available|happening|coming up)\b',
                'EVENTS',
                {},
                0.9
            ),
            
            # BUY_TICKET command patterns
            (
                r'\b(?:buy|purchase|get)\s+(?:a\s+)?ticket\s+(?:for\s+)?event\s+(\d+)',
                'BUY_TICKET',
                {'event_id': 1},
                1.0
            ),
            (
                r'\bticket\s+(?:for\s+)?event\s+(\d+)',
                'BUY_TICKET',
                {'event_id': 1},
                0.9
            ),
            (
                r'\bregister\s+(?:for\s+)?event\s+(\d+)',
                'BUY_TICKET',
                {'event_id': 1},
                0.85
            ),
            
            # FUNDS command patterns
            (
                r'\b(?:show|list|display|get|see)\s+(?:me\s+)?(?:all\s+)?(?:available\s+)?(?:fundraisers?|funds?|campaigns?)\b',
                'FUNDS',
                {},
                1.0
            ),
            (
                r'\b(?:fundraisers?|campaigns?)\s+(?:list|available)\b',
                'FUNDS',
                {},
                0.95
            ),
            (
                r'\bwhat\s+(?:fundraisers?|campaigns?)\s+(?:are\s+)?(?:available|active)\b',
                'FUNDS',
                {},
                0.9
            ),
            
            # CONTRIBUTE command patterns
            (
                r'\b(?:contribute|donate)\s+(\d+(?:\.\d+)?)\s+(?:algo|algos?)\s+to\s+(?:fund|fundraiser|campaign)\s+(\d+)',
                'CONTRIBUTE',
                {'amount': 1, 'fund_id': 2},
                1.0
            ),
            (
                r'\bdonate\s+to\s+(?:fund|fundraiser|campaign)\s+(\d+)\s+(\d+(?:\.\d+)?)\s+(?:algo|algos?)',
                'CONTRIBUTE',
                {'fund_id': 1, 'amount': 2},
                0.95
            ),
            (
                r'\bfund\s+(\d+)\s+contribute\s+(\d+(?:\.\d+)?)',
                'CONTRIBUTE',
                {'fund_id': 1, 'amount': 2},
                0.9
            ),
            
            # SPLIT command patterns
            (
                r'\b(?:split|divide)\s+(?:a\s+)?bill\s+(?:of\s+)?(\d+(?:\.\d+)?)\s+(?:algo|algos?)\s+(?:with|among|between)\s+(.+)',
                'SPLIT',
                {'amount': 1, 'participants': 2},
                1.0
            ),
            (
                r'\bcreate\s+(?:a\s+)?split\s+(?:for\s+)?(\d+(?:\.\d+)?)\s+with\s+(.+)',
                'SPLIT',
                {'amount': 1, 'participants': 2},
                0.95
            ),
            
            # MY_SPLITS command patterns
            (
                r'\b(?:show|list|display|get)\s+(?:my\s+)?splits?\b',
                'MY_SPLITS',
                {},
                1.0
            ),
            (
                r'\bwhat\s+splits?\s+(?:do\s+i\s+have|am\s+i\s+in)\b',
                'MY_SPLITS',
                {},
                0.9
            ),
            
            # PAY_SPLIT command patterns
            (
                r'\bpay\s+(?:my\s+)?(?:share|part)\s+(?:for|in|of)\s+split\s+(\d+)',
                'PAY_SPLIT',
                {'split_id': 1},
                1.0
            ),
            (
                r'\bsettle\s+split\s+(\d+)',
                'PAY_SPLIT',
                {'split_id': 1},
                0.95
            ),
            
            # HELP command patterns
            (
                r'\b(?:help|commands?|what\s+can\s+you\s+do|how\s+to\s+use)\b',
                'HELP',
                {},
                1.0
            ),
        ]
    
    def parse_natural_language(self, text: str) -> Optional[ParsedCommand]:
        """
        Parse natural language text to extract command and parameters
        
        Args:
            text: User's natural language input
            
        Returns:
            ParsedCommand if a match is found, None otherwise
        """
        if not text or not text.strip():
            return None
        
        text_lower = text.lower().strip()
        
        # Try each pattern
        best_match = None
        best_confidence = 0.0
        
        for pattern, command, param_extractors, base_confidence in self.patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                # Extract parameters based on param_extractors
                params = {}
                for param_name, group_idx in param_extractors.items():
                    if group_idx <= len(match.groups()):
                        value = match.group(group_idx).strip()
                        
                        # Clean up phone numbers
                        if param_name == 'phone':
                            value = self._clean_phone_number(value)
                        
                        # Parse participants for SPLIT command
                        elif param_name == 'participants':
                            value = self._parse_participants(value)
                        
                        params[param_name] = value
                
                # Use the highest confidence match
                if base_confidence > best_confidence:
                    best_confidence = base_confidence
                    best_match = ParsedCommand(
                        command=command,
                        params=params,
                        confidence=base_confidence,
                        original_text=text
                    )
        
        return best_match
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and normalize phone number"""
        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Ensure it starts with +
        if not cleaned.startswith('+'):
            # Assume +91 for Indian numbers without country code
            if len(cleaned) == 10:
                cleaned = '+91' + cleaned
            else:
                cleaned = '+' + cleaned
        
        return cleaned
    
    def _parse_participants(self, text: str) -> list:
        """Parse participant phone numbers from text"""
        # Split by common separators
        parts = re.split(r'[,\s]+(?:and|&)?\s*', text)
        
        participants = []
        for part in parts:
            # Extract phone numbers
            phone_match = re.search(r'[\+\d][\d\s\-\(\)]+', part)
            if phone_match:
                participants.append(self._clean_phone_number(phone_match.group()))
        
        return participants


# Global instance
nl_mapper = NaturalLanguageMapper()
