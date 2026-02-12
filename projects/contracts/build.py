"""
Build script for AlgoChat Pay smart contracts
"""
import os
import subprocess


def build_contract(contract_name):
    """Build a single contract"""
    print(f"\n🔨 Building {contract_name}...")
    
    try:
        subprocess.run(
            ["python", f"{contract_name}.py"],
            check=True,
            cwd="."
        )
        print(f"✅ {contract_name} built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build {contract_name}: {e}")
        return False


def main():
    """Build all contracts"""
    print("="*60)
    print("🏗️  BUILDING ALGOCHAT PAY SMART CONTRACTS")
    print("="*60)
    
    contracts = [
        "split_payment",
        "fundraising_pool",
        "ticket_nft"
    ]
    
    results = []
    for contract in contracts:
        success = build_contract(contract)
        results.append((contract, success))
    
    print("\n" + "="*60)
    print("📊 BUILD SUMMARY")
    print("="*60)
    
    for contract, success in results:
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{contract:30} {status}")
    
    all_success = all(success for _, success in results)
    if all_success:
        print("\n🎉 All contracts built successfully!")
        return 0
    else:
        print("\n⚠️  Some contracts failed to build")
        return 1


if __name__ == "__main__":
    exit(main())
