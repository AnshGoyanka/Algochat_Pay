"""
Test WhatsApp notifications for payments and splits
"""
from backend.database import SessionLocal
from backend.services.notification_service import notification_service

db = SessionLocal()

try:
    print("Testing WhatsApp Notification Service\n")
    print("=" * 60)
    
    # Test 1: Payment received notification
    print("\n1. Testing payment received notification...")
    result = notification_service.notify_payment_received(
        receiver_phone="+918237987667",
        sender_phone="+919999999999",
        amount=25.5,
        payment_ref="P12345",
        tx_id="6RKENLBUYXWT5PJ44NEXVQ6Z4BBSTFAMY73GFMLTLX45U74IKRDA"
    )
    print(f"   Result: {'✓ Sent' if result else '✗ Failed'}")
    
    # Test 2: Split bill created notification
    print("\n2. Testing split bill created notification...")
    result = notification_service.notify_split_bill_created(
        participant_phone="+918237987667",
        initiator_phone="+919876543210",
        split_id=1,
        amount_per_person=50.0,
        description="Dinner at Italian Restaurant"
    )
    print(f"   Result: {'✓ Sent' if result else '✗ Failed'}")
    
    # Test 3: Split payment received notification
    print("\n3. Testing split payment received notification...")
    result = notification_service.notify_split_payment_received(
        initiator_phone="+918237987667",
        participant_phone="+919999888877",
        amount=50.0,
        split_id=1,
        is_fully_paid=False
    )
    print(f"   Result: {'✓ Sent' if result else '✗ Failed'}")
    
    # Test 4: Fund contribution notification
    print("\n4. Testing fund contribution notification...")
    result = notification_service.notify_fund_contribution(
        creator_phone="+918237987667",
        contributor_phone="+919876543210",
        amount=100.0,
        fund_title="Heart Surgery for 8-Year-Old",
        total_raised=350.0,
        goal_amount=600.0
    )
    print(f"   Result: {'✓ Sent' if result else '✗ Failed'}")
    
    print("\n" + "=" * 60)
    print("✓ All 4 notification tests completed!")
    print("\nNotification Types Tested:")
    print("  1. Payment Received")
    print("  2. Split Bill Created")
    print("  3. Split Payment Received")
    print("  4. Fund Contribution")
    print("\nCheck your WhatsApp to see the notifications.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
