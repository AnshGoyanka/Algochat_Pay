"""
Fund test wallets from a funding account
Useful for demo preparation
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from backend.algorand.client import algorand_client
from algosdk import mnemonic
import json


def fund_wallet(funder_private_key: str, recipient_address: str, amount: float, label: str):
    """Send ALGO from funder to recipient"""
    print(f"\n💰 Funding {label} ({recipient_address[:8]}...) with {amount} ALGO...")
    
    try:
        tx_id = algorand_client.send_payment(
            sender_private_key=funder_private_key,
            receiver_address=recipient_address,
            amount_algo=amount,
            note=f"Test funding for {label}"
        )
        print(f"   ✅ Success! TX: {tx_id[:16]}...")
        return True
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False


def main():
    """Fund all test wallets"""
    print("=" * 70)
    print("💸 AlgoChat Pay - Test Wallet Funding")
    print("=" * 70)
    
    # Load test wallets
    wallets_file = Path(__file__).parent / "test_wallets.json"
    
    if not wallets_file.exists():
        print("❌ test_wallets.json not found!")
        print("   Run create_test_wallets.py first")
        return
    
    with open(wallets_file, "r") as f:
        test_wallets = json.load(f)
    
    print(f"\n📋 Found {len(test_wallets)} test wallets")
    
    # Get funder credentials
    print("\n🔐 Enter funder wallet mnemonic (25 words):")
    print("   (Get ALGO from: https://bank.testnet.algorand.network/)")
    funder_mnemonic = input("\n> ").strip()
    
    try:
        funder_private_key = mnemonic.to_private_key(funder_mnemonic)
        funder_address = algorand_client.algod_client.account_info(
            algorand_client.algod_client.account_info
        )
    except:
        print("❌ Invalid mnemonic!")
        return
    
    # Amount to send each wallet
    amount_per_wallet = 10.0  # 10 ALGO for testing
    
    print(f"\n💰 Funding each wallet with {amount_per_wallet} ALGO...")
    print("   Press Enter to continue, or Ctrl+C to cancel")
    input()
    
    # Fund each wallet
    success_count = 0
    for wallet in test_wallets:
        success = fund_wallet(
            funder_private_key,
            wallet["address"],
            amount_per_wallet,
            wallet["label"]
        )
        if success:
            success_count += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Funded {success_count}/{len(test_wallets)} wallets successfully!")
    print("=" * 70)
    print("\n🎉 Your test environment is ready!")
    print("   You can now test AlgoChat Pay with these wallets")


if __name__ == "__main__":
    main()
