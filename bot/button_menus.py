"""
Interactive Button Menus for WhatsApp and Telegram
Provides clickable buttons for common commands
"""
from typing import List, Dict, Any


class ButtonMenus:
    """Button layouts for different menu types"""
    
    # Main menu buttons (most common actions)
    MAIN_MENU = [
        {"id": "balance", "title": "💰 Balance"},
        {"id": "history", "title": "📜 History"},
        {"id": "help", "title": "❓ Help"}
    ]
    
    # Quick actions menu
    QUICK_ACTIONS = [
        {"id": "list_events", "title": "🎫 Events"},
        {"id": "list_funds", "title": "💝 Fundraisers"},
        {"id": "my_splits", "title": "💸 My Splits"},
        {"id": "my_tickets", "title": "🎟️ My Tickets"}
    ]
    
    # Financial actions
    FINANCIAL_MENU = [
        {"id": "balance", "title": "💰 Check Balance"},
        {"id": "history", "title": "📜 Transaction History"},
        {"id": "demo_stats", "title": "📊 Demo Stats"}
    ]
    
    # All commands combined (for help screen)
    ALL_COMMANDS = MAIN_MENU + QUICK_ACTIONS
    
    @staticmethod
    def get_telegram_keyboard(buttons: List[Dict[str, str]], columns: int = 2) -> Dict[str, Any]:
        """
        Generate Telegram inline keyboard markup
        
        Args:
            buttons: List of button dicts with 'id' and 'title'
            columns: Number of buttons per row
            
        Returns:
            Telegram inline_keyboard structure
        """
        keyboard = []
        row = []
        
        for i, btn in enumerate(buttons):
            row.append({
                "text": btn["title"],
                "callback_data": btn["id"]
            })
            
            # Create new row after 'columns' buttons
            if (i + 1) % columns == 0:
                keyboard.append(row)
                row = []
        
        # Add remaining buttons
        if row:
            keyboard.append(row)
        
        return {"inline_keyboard": keyboard}
    
    @staticmethod
    def get_telegram_reply_keyboard(buttons: List[Dict[str, str]], columns: int = 2) -> Dict[str, Any]:
        """
        Generate Telegram reply keyboard (persistent buttons at bottom)
        
        Args:
            buttons: List of button dicts with 'id' and 'title'
            columns: Number of buttons per row
            
        Returns:
            Telegram keyboard structure
        """
        keyboard = []
        row = []
        
        for i, btn in enumerate(buttons):
            row.append({"text": btn["title"]})
            
            if (i + 1) % columns == 0:
                keyboard.append(row)
                row = []
        
        if row:
            keyboard.append(row)
        
        return {
            "keyboard": keyboard,
            "resize_keyboard": True,
            "one_time_keyboard": False
        }
    
    @staticmethod
    def get_whatsapp_buttons(buttons: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Generate WhatsApp button format (max 3 buttons)
        
        Args:
            buttons: List of button dicts with 'id' and 'title'
            
        Returns:
            List of WhatsApp button structures
        """
        # WhatsApp supports max 3 buttons per message
        limited_buttons = buttons[:3]
        
        return [
            {
                "type": "reply",
                "reply": {
                    "id": btn["id"],
                    "title": btn["title"][:20]  # Max 20 chars for WhatsApp
                }
            }
            for btn in limited_buttons
        ]
    
    @staticmethod
    def get_whatsapp_list_sections(buttons: List[Dict[str, str]], section_title: str = "Quick Actions") -> Dict[str, Any]:
        """
        Generate WhatsApp list message format (supports more options)
        
        Args:
            buttons: List of button dicts with 'id' and 'title'
            section_title: Title for the section
            
        Returns:
            WhatsApp list message structure
        """
        rows = [
            {
                "id": btn["id"],
                "title": btn["title"][:24],  # Max 24 chars
                "description": ""
            }
            for btn in buttons
        ]
        
        return {
            "button": "Menu",
            "sections": [
                {
                    "title": section_title,
                    "rows": rows
                }
            ]
        }


button_menus = ButtonMenus()
