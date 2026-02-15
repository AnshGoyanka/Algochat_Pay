"""
WhatsApp command parser
Extracts intent and parameters from user messages
"""
import re
from typing import Optional, Dict, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CommandType(str, Enum):
    """Supported bot commands"""
    HELP = "help"
    MENU = "menu"
    BALANCE = "balance"
    PAY = "pay"
    SPLIT = "split"
    PAY_SPLIT = "pay_split"
    VIEW_SPLIT = "view_split"
    MY_SPLITS = "my_splits"
    CREATE_FUND = "create_fund"
    CONTRIBUTE = "contribute"
    VIEW_FUND = "view_fund"
    LIST_FUNDS = "list_funds"
    BUY_TICKET = "buy_ticket"
    VERIFY_TICKET = "verify_ticket"
    MY_TICKETS = "my_tickets"
    LIST_EVENTS = "list_events"
    HISTORY = "history"
    DEMO_STATS = "demo_stats"
    # Payment Commitments
    CREATE_COMMITMENT = "create_commitment"
    COMMIT_FUNDS = "commit_funds"
    VIEW_COMMITMENT = "view_commitment"
    CANCEL_COMMITMENT = "cancel_commitment"
    ADD_PARTICIPANT = "add_participant"
    RELIABILITY = "reliability"
    MY_COMMITMENTS = "my_commitments"
    UNKNOWN = "unknown"


class ParsedCommand:
    """Structured command data"""
    
    def __init__(self, command_type: CommandType, params: Dict = None, raw_text: str = ""):
        self.type = command_type
        self.params = params or {}
        self.raw_text = raw_text
    
    def __repr__(self):
        return f"<ParsedCommand {self.type}: {self.params}>"


class CommandParser:
    """
    Natural language parser for WhatsApp messages
    Extracts intent and parameters from user text
    """
    
    # Command patterns (case-insensitive)
    PATTERNS = {
        CommandType.HELP: [
            r"^(help|start|hi|hello|menu)$",
        ],
        CommandType.BALANCE: [
            r"^(balance|bal|wallet|show balance)$",
        ],
        CommandType.PAY: [
            r"^pay\s+(\d+\.?\d*)\s+(?:algo\s+)?to\s+(\+\d+)",
            r"^send\s+(\d+\.?\d*)\s+(?:algo\s+)?to\s+(\+\d+)",
        ],
        CommandType.SPLIT: [
            r"^split\s+(\d+\.?\d*)\s+(?:algo\s+)?(.+?)\s+with\s+(.+)",
        ],
        CommandType.PAY_SPLIT: [
            r"^pay split\s+(\d+)$",
        ],
        CommandType.VIEW_SPLIT: [
            r"^(?:view|show)\s+split\s+(\d+)$",
        ],
        CommandType.MY_SPLITS: [
            r"^(?:my splits|splits)$",
        ],
        CommandType.CREATE_FUND: [
            r"^create fund\s+(.+?)\s+goal\s+(\d+\.?\d*)\s+(?:algo)?",
        ],
        CommandType.CONTRIBUTE: [
            r"^contribute\s+(\d+\.?\d*)\s+(?:algo\s+)?to\s+fund\s+(\d+)",
            r"^fund\s+(\d+)\s+(\d+\.?\d*)\s+(?:algo)?",
        ],
        CommandType.VIEW_FUND: [
            r"^(?:view|show)\s+fund\s+(\d+)",
        ],
        CommandType.LIST_FUNDS: [
            r"^(?:list|show)\s+funds?$",
            r"^funds?$",
        ],
        CommandType.BUY_TICKET: [
            r"^buy ticket\s+(\d+)$",  # buy ticket 1
            r"^buy ticket\s+(.+)",     # buy ticket EventName
        ],
        CommandType.VERIFY_TICKET: [
            r"^verify ticket\s+(.+)",
        ],
        CommandType.MY_TICKETS: [
            r"^(?:my tickets|tickets)$",
        ],
        CommandType.LIST_EVENTS: [
            r"^(?:list|show)\s+events?$",
            r"^events?$",
        ],
        CommandType.HISTORY: [
            r"^(?:history|transactions)$",
        ],
        CommandType.DEMO_STATS: [
            r"^demo stats$",
            r"^demo$",
            r"^stats$",
            r"^show stats$",
        ],
        # Payment Commitments
        CommandType.CREATE_COMMITMENT: [
            r"^lock create\s+(.+?)\s+(\d+\.?\d*)\s+(\d+)\s+(\d+)$",  # lock create "Goa Trip" 500 5 7
            r"^/lock\s+create\s+(.+?)\s+(\d+\.?\d*)\s+(\d+)\s+(\d+)$",
        ],
        CommandType.COMMIT_FUNDS: [
            r"^commit\s+(\d+)$",  # commit 123
            r"^/commit\s+(\d+)$",
            r"^lock\s+(\d+)$",
        ],
        CommandType.VIEW_COMMITMENT: [
            r"^commitment\s+(\d+)$",  # commitment 123
            r"^/commitment\s+(\d+)$",
            r"^show commitment\s+(\d+)$",
        ],
        CommandType.CANCEL_COMMITMENT: [
            r"^cancel\s+(\d+)$",  # cancel 123
            r"^/cancel\s+(\d+)$",
            r"^cancel commitment\s+(\d+)$",
        ],
        CommandType.ADD_PARTICIPANT: [
            r"^add\s+(\d+)\s+(\+\d+)$",  # add 123 +919999999999
            r"^/add\s+(\d+)\s+(\+\d+)$",
        ],
        CommandType.RELIABILITY: [
            r"^reliability$",
            r"^/reliability$",
            r"^my reliability$",
            r"^score$",
        ],
        CommandType.MY_COMMITMENTS: [
            r"^my commitments?$",
            r"^/commitments?$",
            r"^commitments?$",
        ],
    }
    
    def parse(self, message: str) -> ParsedCommand:
        """
        Parse WhatsApp message into structured command
        
        Args:
            message: Raw message text from user
        
        Returns:
            ParsedCommand object
        """
        # Normalize message
        text = message.strip().lower()
        
        # Try to match patterns
        for command_type, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.match(pattern, text, re.IGNORECASE)
                if match:
                    params = self._extract_params(command_type, match, message)
                    return ParsedCommand(command_type, params, message)
        
        # No match found
        return ParsedCommand(CommandType.UNKNOWN, {}, message)
    
    def _extract_params(self, command_type: CommandType, match: re.Match, original_text: str) -> Dict:
        """Extract parameters based on command type"""
        
        if command_type == CommandType.PAY:
            return {
                "amount": float(match.group(1)),
                "receiver_phone": match.group(2)
            }
        
        elif command_type == CommandType.SPLIT:
            amount = float(match.group(1))
            description = match.group(2).strip()
            
            # Extract phone numbers from "with" clause
            with_clause = match.group(3)
            phones = self._extract_phone_numbers(with_clause)
            
            return {
                "amount": amount,
                "description": description,
                "participants": phones
            }
        
        elif command_type == CommandType.CREATE_FUND:
            return {
                "title": match.group(1).strip(),
                "goal_amount": float(match.group(2))
            }
        
        elif command_type == CommandType.CONTRIBUTE:
            # Check which pattern matched
            if "fund" in match.group(0).lower():
                # Pattern: contribute X to fund Y
                return {
                    "amount": float(match.group(1)),
                    "fund_id": int(match.group(2))
                }
            else:
                # Pattern: fund Y X
                return {
                    "fund_id": int(match.group(1)),
                    "amount": float(match.group(2))
                }
        
        elif command_type == CommandType.VIEW_FUND:
            return {
                "fund_id": int(match.group(1))
            }
        
        elif command_type == CommandType.BUY_TICKET:
            event_identifier = match.group(1).strip()
            # Check if it's a number (event ID) or name
            if event_identifier.isdigit():
                return {
                    "event_id": int(event_identifier)
                }
            else:
                return {
                    "event_name": event_identifier
                }
        
        elif command_type == CommandType.VERIFY_TICKET:
            return {
                "ticket_number": match.group(1).strip().upper()
            }
        
        elif command_type == CommandType.PAY_SPLIT:
            return {
                "split_bill_id": int(match.group(1))
            }
        
        elif command_type == CommandType.VIEW_SPLIT:
            return {
                "split_bill_id": int(match.group(1))
            }
        
        # Payment Commitments
        elif command_type == CommandType.CREATE_COMMITMENT:
            return {
                "title": match.group(1).strip(),
                "amount": float(match.group(2)),
                "participants": int(match.group(3)),
                "days": int(match.group(4))
            }
        
        elif command_type == CommandType.COMMIT_FUNDS:
            return {
                "commitment_id": int(match.group(1))
            }
        
        elif command_type == CommandType.VIEW_COMMITMENT:
            return {
                "commitment_id": int(match.group(1))
            }
        
        elif command_type == CommandType.CANCEL_COMMITMENT:
            return {
                "commitment_id": int(match.group(1))
            }
        
        elif command_type == CommandType.ADD_PARTICIPANT:
            return {
                "commitment_id": int(match.group(1)),
                "phone": match.group(2)
            }
        
        return {}
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract all phone numbers from text"""
        # Pattern: +followed by digits
        pattern = r'\+\d{10,15}'
        phones = re.findall(pattern, text)
        return phones
    
    def get_help_text(self) -> str:
        """Get help menu text"""
        return """
🏦 *AlgoChat Pay - Campus Wallet*

*Available Commands:*

💰 *Balance & Wallet*
• `balance` - Check your wallet balance

💸 *Payments*
• `pay 50 ALGO to +91XXXXXXXXXX` - Send ALGO
• `split 400 ALGO dinner with +91XXX +91YYY` - Split bill
• `pay split 1` - Pay your share of split bill
• `my splits` - View pending split bills

🔒 *Payment Commitments* ✨ NEW!
• `make a goa trip` - Create via conversation (easy!)
• `/lock create Trip 500 5 7` - Or use command
• `/commit 1` - Lock your funds
• `/status 1` - View commitment status
• `/commitments` - Your active commitments
• `/reliability` - Your payment reputation score

🎫 *Event Tickets*
• `list events` - See all upcoming events
• `buy ticket TechFest 2026` - Purchase event ticket (NFT)
• `my tickets` - View your tickets
• `verify ticket TIX-ABC123` - Verify ticket authenticity

🎯 *Fundraising*
• `list funds` - See active campaigns
• `create fund Trip goal 500 ALGO` - Start fundraising
• `contribute 50 ALGO to fund 1` - Contribute to fund
• `view fund 1` - Check fund details

📊 *History*
• `history` - View transaction history

💡 *Pro Tip:* Just say "make a [title] trip" and I'll guide you!

Need help? Just type `help` anytime!
        """.strip()


# Global parser instance
command_parser = CommandParser()
