"""
Test WhatsApp button integration
Shows how messages will look with buttons
"""
from bot.button_menus import button_menus
from bot.response_templates import response_templates


def test_whatsapp_button_format():
    """Test how WhatsApp messages with buttons will look"""
    
    print("=" * 80)
    print("WhatsApp Button Message Preview")
    print("=" * 80)
    
    # Simulate balance response with buttons
    balance_text = response_templates.balance_info(
        phone="+918237987667",
        address="3G76 6 BPMUH...NLZ 6 UUXQ",
        balance=0.0000
    )
    
    # Add button options
    buttons = button_menus.get_whatsapp_buttons(button_menus.MAIN_MENU)
    
    options_text = "\n\n🔘 *Quick Actions:*\n"
    for i, btn in enumerate(buttons, 1):
        options_text += f"\n{i}️⃣ {btn['reply']['title']}"
    
    footer = "\n\n💡 _Reply with number or type command_"
    full_message = balance_text + options_text + footer
    
    print("\n" + full_message)
    print("\n" + "=" * 80)
    
    # Simulate menu response
    print("\nMenu Response Preview:")
    print("=" * 80)
    
    menu_text = response_templates.quick_menu()
    
    options_text2 = "\n\n🔘 *Quick Actions:*\n"
    for i, btn in enumerate(buttons, 1):
        options_text2 += f"\n{i}️⃣ {btn['reply']['title']}"
    
    full_menu = menu_text + options_text2 + footer
    print("\n" + full_menu)
    print("\n" + "=" * 80)
    
    print("\n✅ Button format test complete!")
    print("\nUser can:")
    print("  • Reply with '1' for Balance")
    print("  • Reply with '2' for History")
    print("  • Reply with '3' for Help")
    print("  • Or type any command directly")


if __name__ == "__main__":
    test_whatsapp_button_format()
