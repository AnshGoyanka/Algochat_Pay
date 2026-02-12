"""
Create test wallets on Algorand TestNet
Useful for demo and testing
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.algorand.client import algorand_client
from backend.security.encryption import encryption_service
from backend.database import SessionLocal, init_db
from backend.models.user import User
import json


def create_test_wallet(db, phone_number: str, label: str) -> dict:
    """Create a test wallet and save to database"""
    print(f"\n🔨 Creating wallet for {label} ({phone_number})...")
    
    # Create Algorand wallet
    private_key, address, mnemonic = algorand_client.create_wallet()
    
    # Encrypt private key
    encrypted_key = encryption_service.encrypt_private_key(private_key)
    
    # Save to database
    user = User(
        phone_number=phone_number,
        wallet_address=address,
        encrypted_private_key=encrypted_key
    )
    
    db.add(user)
    db.commit()
    
    wallet_info = {
        "label": label,
        "phone": phone_number,
        "address": address,
        "mnemonic": mnemonic
    }
    
    print(f"✅ Wallet created!")
    print(f"   Address: {address}")
    print(f"   Mnemonic: {mnemonic}")
    
    return wallet_info


def main():
    """Create test wallets for demo"""
    print("=" * 70)
    print("🏦 AlgoChat Pay - Test Wallet Generator")
    print("=" * 70)
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    # Create test wallets
    test_wallets = []
    
    wallets_to_create = [
        ("+919876543210", "Alice (Student)"),
        ("+919876543211", "Bob (Friend 1)"),
        ("+919876543212", "Carol (Friend 2)"),
        ("+919876543213", "Dave (Event Organizer)"),
        ("+919876543214", "Eve (Faculty)"),
    ]
    
    for phone, label in wallets_to_create:
        wallet = create_test_wallet(db, phone, label)
        test_wallets.append(wallet)
    
    # Save to file
    output_file = Path(__file__).parent / "test_wallets.json"
    with open(output_file, "w") as f:
        json.dump(test_wallets, f, indent=2)
    
    print("\n" + "=" * 70)
    print("✅ ALL TEST WALLETS CREATED!")
    print("=" * 70)
    print(f"\n📄 Wallet details saved to: {output_file}")
    print("\n⚠️  IMPORTANT: Fund these wallets using TestNet dispenser:")
    print("   https://bank.testnet.algorand.network/")
    print("\nWallets to fund:")
    for wallet in test_wallets:
        print(f"   • {wallet['address']} ({wallet['label']})")
    
    db.close()


if __name__ == "__main__":
    main()
