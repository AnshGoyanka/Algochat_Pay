"""
Test script for Natural Language Mapper
"""
from backend.services.nl_mapper import nl_mapper


def test_nl_mapper():
    """Test various natural language commands"""
    
    test_cases = [
        # Balance queries
        "show me my balance",
        "check balance",
        "what's my balance",
        "how much algo do i have",
        
        # History queries
        "show my transaction history",
        "list my recent transactions",
        "what have i sent",
        
        # Payment commands
        "send 50 algo to +919876543210",
        "pay +919876543210 25.5 algos",
        "transfer 100 to +1234567890",
        
        # Events
        "show all events",
        "list events",
        "what events are available",
        
        # Buy ticket
        "buy ticket for event 5",
        "purchase a ticket event 3",
        "register for event 1",
        
        # Fundraisers
        "show all fundraisers",
        "list funds",
        "what campaigns are active",
        
        # Contribute
        "contribute 100 algo to fund 2",
        "donate to fundraiser 5 50 algos",
        "fund 3 contribute 25",
        
        # Split bill
        "split bill 200 algo with +919876543210 +919999999999",
        "create a split for 150 with +91XXXXXXXXXX +91YYYYYYYYYY",
        
        # My splits
        "show my splits",
        "what splits am i in",
        
        # Pay split
        "pay my share for split 5",
        "settle split 3",
        
        # Help
        "help",
        "what can you do",
        
        # Unknown (should not match)
        "hello how are you",
        "this is random text",
    ]
    
    print("=" * 80)
    print("Natural Language Mapper Test Results")
    print("=" * 80)
    
    for text in test_cases:
        result = nl_mapper.parse_natural_language(text)
        
        print(f"\nInput: {text}")
        if result:
            print(f"[MATCH] Command: {result.command}")
            print(f"  Confidence: {result.confidence:.2f}")
            if result.params:
                print(f"  Params: {result.params}")
        else:
            print("[NO MATCH]")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_nl_mapper()
