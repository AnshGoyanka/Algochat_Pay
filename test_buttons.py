"""
Test script for button menus
"""
import sys
import io
from bot.button_menus import button_menus
import json

# Set UTF-8 encoding for console output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_telegram_keyboards():
    """Test Telegram keyboard generation"""
    print("=" * 80)
    print("TELEGRAM INLINE KEYBOARD TEST")
    print("=" * 80)
    
    # Test main menu
    keyboard = button_menus.get_telegram_keyboard(button_menus.MAIN_MENU, columns=3)
    print("\nMain Menu (3 columns):")
    print(json.dumps(keyboard, indent=2))
    
    # Test all commands
    keyboard_all = button_menus.get_telegram_keyboard(button_menus.ALL_COMMANDS, columns=3)
    print("\nAll Commands (3 columns):")
    print(json.dumps(keyboard_all, indent=2))
    
    # Test reply keyboard
    reply_kb = button_menus.get_telegram_reply_keyboard(button_menus.MAIN_MENU, columns=3)
    print("\nReply Keyboard (persistent):")
    print(json.dumps(reply_kb, indent=2))


def test_whatsapp_buttons():
    """Test WhatsApp button generation"""
    print("\n" + "=" * 80)
    print("WHATSAPP BUTTONS TEST")
    print("=" * 80)
    
    # Test WhatsApp buttons (max 3)
    buttons = button_menus.get_whatsapp_buttons(button_menus.MAIN_MENU)
    print("\nQuick Reply Buttons (max 3):")
    print(json.dumps(buttons, indent=2))
    
    # Test WhatsApp list message
    list_msg = button_menus.get_whatsapp_list_sections(
        button_menus.ALL_COMMANDS, 
        section_title="Quick Actions"
    )
    print("\nList Message:")
    print(json.dumps(list_msg, indent=2))


def test_menu_response():
    """Test the quick menu response"""
    from bot.response_templates import response_templates
    
    print("\n" + "=" * 80)
    print("QUICK MENU RESPONSE")
    print("=" * 80)
    
    menu_text = response_templates.quick_menu()
    print("\n" + menu_text)


if __name__ == "__main__":
    test_telegram_keyboards()
    test_whatsapp_buttons()
    test_menu_response()
    
    print("\n" + "=" * 80)
    print("✓ All button menu tests passed!")
    print("=" * 80)
