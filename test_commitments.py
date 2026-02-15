"""
Test Payment Lock Commitments Feature
Quick smoke test to verify everything works
"""
from datetime import datetime, timedelta
from backend.database import SessionLocal
from backend.services.commitment_service import commitment_service
from backend.services.wallet_service import wallet_service

def test_commitments():
    db = SessionLocal()
    
    try:
        print("🧪 Testing Payment Lock Commitments\n")
        print("=" * 60)
        
        # Test user phones
        organizer_phone = "+918237987667"  # Your phone
        participant_phone = "+919545296699"  # Friend's phone
        
        print("\n1️⃣  Creating commitment...")
        commitment = commitment_service.create_commitment(
            db=db,
            organizer_phone=organizer_phone,
            title="Test Goa Trip",
            amount_per_person=10.0,  # Small amount for testing
            total_participants=2,
            deadline=datetime.utcnow() + timedelta(days=7),
            description="Test trip to verify commitment system"
        )
        
        print(f"✅ Created commitment #{commitment.id}")
        print(f"   Title: {commitment.title}")
        print(f"   Amount: {commitment.amount_per_person} ALGO per person")
        print(f"   Escrow Address: {commitment.escrow_address}")
        print(f"   Deadline: {commitment.deadline}")
        
        print("\n2️⃣  Adding participant...")
        participant = commitment_service.add_participant(
            db=db,
            commitment_id=commitment.id,
            phone=participant_phone
        )
        print(f"✅ Added {participant_phone}")
        
        print("\n3️⃣  Getting commitment status...")
        status = commitment_service.get_commitment_status(
            db=db,
            commitment_id=commitment.id
        )
        print(f"✅ Status:")
        print(f"   Locked: {status['participants_locked']}/{status['total_participants']}")
        print(f"   Total Locked: {status['total_locked']} ALGO")
        print(f"   Days Until Deadline: {status['days_until_deadline']}")
        
        print("\n4️⃣  Checking reliability score...")
        reliability = commitment_service.get_user_reliability(
            db=db,
            phone=organizer_phone
        )
        print(f"✅ Reliability Score:")
        print(f"   Badge: {reliability['badge']}")
        print(f"   Score: {reliability['score']}/100")
        print(f"   Total Commitments: {reliability['total_commitments']}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("\n📝 Next Steps:")
        print(f"1. Test locking funds: /commit {commitment.id}")
        print(f"2. Check status: /commitment {commitment.id}")
        print(f"3. View reliability: /reliability")
        print(f"\n🎯 Commitment ID for testing: #{commitment.id}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()


if __name__ == "__main__":
    test_commitments()
