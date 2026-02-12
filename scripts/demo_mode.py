"""
Demo Mode Tools
Prepares environment for reliable hackathon demo
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal
from backend.services.wallet_service import wallet_service
from backend.algorand.client import algorand_client
from backend.utils.production_logging import ProductionLogger

logger = ProductionLogger.get_logger(__name__)


class DemoSetup:
    """
    Demo environment setup and validation
    """
    
    DEMO_USERS = [
        "+14155552001",  # Alice
        "+14155552002",  # Bob
        "+14155552003",  # Charlie
        "+14155552004",  # Organizer
    ]
    
    def __init__(self):
        self.db = SessionLocal()
    
    def create_demo_wallets(self):
        """
        Pre-create wallets for demo users
        Ensures instant wallet access during demo
        """
        print("🎬 Creating demo wallets...")
        
        wallets_created = []
        
        for phone in self.DEMO_USERS:
            try:
                user, created = wallet_service.get_or_create_wallet(self.db, phone)
                
                if created:
                    print(f"  ✅ Created wallet for {phone}: {user.wallet_address}")
                else:
                    print(f"  ♻️  Wallet already exists for {phone}")
                
                wallets_created.append({
                    "phone": phone,
                    "address": user.wallet_address
                })
                
            except Exception as e:
                print(f"  ❌ Failed to create wallet for {phone}: {e}")
        
        return wallets_created
    
    def check_wallet_balances(self, wallets):
        """
        Check balances and provide funding instructions
        """
        print("\n💰 Checking wallet balances...")
        
        needs_funding = []
        
        for wallet in wallets:
            try:
                balance = algorand_client.get_balance(wallet["address"])
                
                if balance < 10.0:
                    print(f"  ⚠️  {wallet['phone']}: {balance:.2f} ALGO (LOW - needs funding)")
                    needs_funding.append(wallet)
                else:
                    print(f"  ✅ {wallet['phone']}: {balance:.2f} ALGO")
                    
            except Exception as e:
                print(f"  ❌ Failed to check balance for {wallet['phone']}: {e}")
        
        if needs_funding:
            print("\n📥 Fund these wallets using Algorand TestNet Dispenser:")
            print("   https://bank.testnet.algorand.network/")
            print("\n   Addresses to fund:")
            for wallet in needs_funding:
                print(f"   • {wallet['address']}")
        
        return needs_funding
    
    def verify_algorand_connection(self):
        """
        Verify connection to Algorand network
        """
        print("\n🔗 Verifying Algorand connection...")
        
        try:
            status = algorand_client.algod_client.status()
            last_round = status.get("last-round", 0)
            
            print(f"  ✅ Connected to Algorand TestNet")
            print(f"  📊 Last round: {last_round}")
            print(f"  ⏱️  Time since last round: {status.get('time-since-last-round', 0) / 1_000_000_000:.2f}s")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Failed to connect to Algorand: {e}")
            return False
    
    def test_demo_flow(self):
        """
        Test a complete demo transaction
        """
        print("\n🧪 Testing demo flow...")
        
        try:
            # Get two demo wallets
            alice = self.DEMO_USERS[0]
            bob = self.DEMO_USERS[1]
            
            alice_user = wallet_service.get_user_by_phone(self.db, alice)
            bob_user = wallet_service.get_user_by_phone(self.db, bob)
            
            if not alice_user or not bob_user:
                print("  ⚠️  Demo users not found. Run create_demo_wallets first.")
                return False
            
            # Check Alice's balance
            alice_balance = algorand_client.get_balance(alice_user.wallet_address)
            
            if alice_balance < 1.0:
                print(f"  ⚠️  Alice's balance ({alice_balance:.2f} ALGO) too low for test")
                return False
            
            print(f"  ✅ Demo users ready")
            print(f"  💰 Alice has {alice_balance:.2f} ALGO")
            print(f"  👥 Alice: {alice} ({alice_user.wallet_address[:20]}...)")
            print(f"  👥 Bob: {bob} ({bob_user.wallet_address[:20]}...)")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Demo flow test failed: {e}")
            return False
    
    def generate_demo_script(self, wallets):
        """
        Generate a demo script with pre-filled commands
        """
        print("\n📝 Demo Script:")
        print("=" * 60)
        print("\n**Setup:**")
        print(f"1. Alice: {self.DEMO_USERS[0]}")
        print(f"2. Bob: {self.DEMO_USERS[1]}")
        print(f"3. Charlie: {self.DEMO_USERS[2]}")
        print(f"4. Organizer: {self.DEMO_USERS[3]}")
        
        print("\n**Demo Flow:**")
        print("\n1️⃣  Show Wallet Creation (Alice):")
        print(f"   Message: balance")
        print(f"   Expected: Shows Alice's wallet address and balance")
        
        print("\n2️⃣  Send Payment (Alice → Bob):")
        print(f"   Message: send {self.DEMO_USERS[1]} 5")
        print(f"   Expected: Transaction confirmed in ~5 seconds")
        
        print("\n3️⃣  Split Bill (Alice, Bob, Charlie):")
        print(f"   Message: split 30 {self.DEMO_USERS[1]} {self.DEMO_USERS[2]} dinner")
        print(f"   Expected: Bill split created, each pays 10 ALGO")
        
        print("\n4️⃣  Create Fundraiser (Organizer):")
        print(f"   Message: fund create 100 Help Campus Food Bank")
        print(f"   Expected: Fundraiser created with ID")
        
        print("\n5️⃣  Donate to Fund (Alice):")
        print(f"   Message: contribute 20 to fund 1")
        print(f"   Expected: Contribution recorded, progress shown")
        
        print("\n6️⃣  Buy Ticket (Alice):")
        print(f"   Message: ticket buy TechFest 5")
        print(f"   Expected: NFT ticket minted")
        
        print("\n7️⃣  Check Transaction History:")
        print(f"   Message: history")
        print(f"   Expected: All transactions displayed")
        
        print("\n" + "=" * 60)
    
    def run_full_setup(self):
        """
        Run complete demo setup
        """
        print("\n" + "🎬" * 20)
        print("ALGOCHAT PAY - DEMO SETUP")
        print("🎬" * 20 + "\n")
        
        # Step 1: Verify Algorand
        if not self.verify_algorand_connection():
            print("\n❌ Cannot proceed without Algorand connection")
            return False
        
        # Step 2: Create wallets
        wallets = self.create_demo_wallets()
        
        if not wallets:
            print("\n❌ No wallets created")
            return False
        
        # Step 3: Check balances
        needs_funding = self.check_wallet_balances(wallets)
        
        # Step 4: Test demo flow
        self.test_demo_flow()
        
        # Step 5: Generate script
        self.generate_demo_script(wallets)
        
        print("\n✅ Demo setup complete!")
        
        if needs_funding:
            print("\n⚠️  WARNING: Some wallets need funding before demo")
            print("   Fund them at: https://bank.testnet.algorand.network/")
        else:
            print("\n🎉 All wallets funded and ready!")
        
        return True
    
    def cleanup(self):
        """Cleanup database connection"""
        self.db.close()


def main():
    """
    Main demo setup script
    
    Usage:
        python scripts/demo_mode.py
    """
    demo = DemoSetup()
    
    try:
        success = demo.run_full_setup()
        
        if success:
            print("\n🚀 Ready for demo!")
            print("\nNext steps:")
            print("1. Start the backend: python -m uvicorn backend.main:app --reload")
            print("2. Test WhatsApp webhook with ngrok")
            print("3. Follow the demo script above")
        else:
            print("\n❌ Setup incomplete. Fix errors and try again.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        demo.cleanup()


if __name__ == "__main__":
    main()
