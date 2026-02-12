"""
Demo Safe Mode Configuration
When FINAL_DEMO_MODE=true, system enters protective mode:
- Disable risky operations
- Use safe test wallets
- Freeze metrics
- Disable high-value transactions
"""
from typing import Optional, Dict, Any
import os
from datetime import datetime


class DemoSafeMode:
    """
    Demo Safe Mode Manager
    Protects production data during live demos
    """
    
    @staticmethod
    def is_enabled() -> bool:
        """Check if demo safe mode is enabled"""
        return os.getenv("FINAL_DEMO_MODE", "false").lower() in ("true", "1", "yes")
    
    @staticmethod
    def get_max_transaction_amount() -> float:
        """Get max transaction amount allowed in demo mode"""
        if DemoSafeMode.is_enabled():
            return float(os.getenv("DEMO_MAX_TRANSACTION", "50.0"))
        return float("inf")  # No limit in normal mode
    
    @staticmethod
    def get_safe_wallet_addresses() -> list:
        """Get list of whitelisted demo wallet addresses"""
        if DemoSafeMode.is_enabled():
            wallets = os.getenv("DEMO_SAFE_WALLETS", "")
            if wallets:
                return [w.strip() for w in wallets.split(",")]
        return []
    
    @staticmethod
    def should_freeze_metrics() -> bool:
        """Check if metrics should be frozen"""
        return DemoSafeMode.is_enabled()
    
    @staticmethod
    def allow_blockchain_writes() -> bool:
        """Check if blockchain write operations are allowed"""
        if DemoSafeMode.is_enabled():
            return os.getenv("DEMO_ALLOW_BLOCKCHAIN_WRITES", "false").lower() in ("true", "1", "yes")
        return True
    
    @staticmethod
    def get_rate_limit_multiplier() -> float:
        """Get rate limit multiplier for demo mode"""
        if DemoSafeMode.is_enabled():
            return float(os.getenv("DEMO_RATE_LIMIT_MULTIPLIER", "0.5"))
        return 1.0
    
    @staticmethod
    def validate_transaction(
        amount: float,
        sender_wallet: str,
        recipient_wallet: str
    ) -> Dict[str, Any]:
        """
        Validate transaction against demo safe mode rules
        
        Returns:
            {
                "allowed": bool,
                "reason": str,
                "modified_amount": float (if reduced),
                "warnings": List[str]
            }
        """
        result = {
            "allowed": True,
            "reason": "",
            "modified_amount": amount,
            "warnings": []
        }
        
        if not DemoSafeMode.is_enabled():
            return result
        
        # Check transaction amount
        max_amount = DemoSafeMode.get_max_transaction_amount()
        if amount > max_amount:
            result["allowed"] = False
            result["reason"] = f"Transaction amount {amount} exceeds demo limit {max_amount}"
            result["modified_amount"] = max_amount
            result["warnings"].append(f"Amount capped at {max_amount} ALGO for demo safety")
        
        # Check wallet whitelist
        safe_wallets = DemoSafeMode.get_safe_wallet_addresses()
        if safe_wallets:
            if sender_wallet not in safe_wallets and recipient_wallet not in safe_wallets:
                result["allowed"] = False
                result["reason"] = "Neither sender nor recipient is a whitelisted demo wallet"
                result["warnings"].append("Only whitelisted wallets allowed in demo mode")
        
        # Check blockchain writes
        if not DemoSafeMode.allow_blockchain_writes():
            result["allowed"] = False
            result["reason"] = "Blockchain writes disabled in demo mode"
            result["warnings"].append("Transaction simulated only - not written to blockchain")
        
        return result
    
    @staticmethod
    def get_configuration() -> Dict[str, Any]:
        """Get current demo safe mode configuration"""
        return {
            "enabled": DemoSafeMode.is_enabled(),
            "max_transaction_amount": DemoSafeMode.get_max_transaction_amount(),
            "safe_wallet_count": len(DemoSafeMode.get_safe_wallet_addresses()),
            "metrics_frozen": DemoSafeMode.should_freeze_metrics(),
            "blockchain_writes_allowed": DemoSafeMode.allow_blockchain_writes(),
            "rate_limit_multiplier": DemoSafeMode.get_rate_limit_multiplier(),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def print_status():
        """Print demo safe mode status to console"""
        config = DemoSafeMode.get_configuration()
        
        print("\n" + "="*80)
        print("DEMO SAFE MODE STATUS")
        print("="*80 + "\n")
        
        if config["enabled"]:
            print("🛡️  DEMO SAFE MODE: ENABLED")
            print(f"   Max Transaction: {config['max_transaction_amount']} ALGO")
            print(f"   Safe Wallets: {config['safe_wallet_count']} configured")
            print(f"   Metrics Frozen: {'YES' if config['metrics_frozen'] else 'NO'}")
            print(f"   Blockchain Writes: {'ALLOWED' if config['blockchain_writes_allowed'] else 'DISABLED'}")
            print(f"   Rate Limit: {config['rate_limit_multiplier']}x normal")
        else:
            print("⚠️  DEMO SAFE MODE: DISABLED")
            print("   Running in normal production mode")
            print("   Set FINAL_DEMO_MODE=true to enable protection")
        
        print("\n" + "="*80 + "\n")


class DemoSafeModeMiddleware:
    """
    FastAPI middleware for demo safe mode
    Intercepts requests and applies safety rules
    """
    
    @staticmethod
    def check_demo_mode_headers() -> Dict[str, str]:
        """Get headers to add to responses in demo mode"""
        if DemoSafeMode.is_enabled():
            return {
                "X-Demo-Mode": "true",
                "X-Demo-Max-Transaction": str(DemoSafeMode.get_max_transaction_amount()),
                "X-Demo-Metrics-Frozen": str(DemoSafeMode.should_freeze_metrics()).lower()
            }
        return {}
    
    @staticmethod
    def validate_payment_request(amount: float, sender: str, recipient: str) -> Dict[str, Any]:
        """
        Validate payment request in demo mode
        Call this before processing any payment
        """
        return DemoSafeMode.validate_transaction(amount, sender, recipient)


def main():
    """CLI for checking demo safe mode status"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Demo Safe Mode Configuration"
    )
    
    parser.add_argument(
        "--enable",
        action="store_true",
        help="Print instructions to enable demo safe mode"
    )
    
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show configuration in JSON format"
    )
    
    args = parser.parse_args()
    
    if args.enable:
        print("\n" + "="*80)
        print("HOW TO ENABLE DEMO SAFE MODE")
        print("="*80 + "\n")
        print("1. Set environment variable before starting server:")
        print("   export FINAL_DEMO_MODE=true")
        print("")
        print("2. Optional: Configure additional safety settings:")
        print("   export DEMO_MAX_TRANSACTION=50.0          # Max ALGO per transaction")
        print("   export DEMO_SAFE_WALLETS=wallet1,wallet2  # Whitelisted wallets")
        print("   export DEMO_ALLOW_BLOCKCHAIN_WRITES=false # Disable blockchain writes")
        print("   export DEMO_RATE_LIMIT_MULTIPLIER=0.5     # Stricter rate limits")
        print("")
        print("3. Start server:")
        print("   uvicorn backend.main:app --reload")
        print("")
        print("4. Verify demo mode is active:")
        print("   python backend/utils/demo_safe_mode.py")
        print("\n" + "="*80 + "\n")
    
    elif args.config:
        import json
        config = DemoSafeMode.get_configuration()
        print(json.dumps(config, indent=2))
    
    else:
        DemoSafeMode.print_status()


if __name__ == "__main__":
    main()
