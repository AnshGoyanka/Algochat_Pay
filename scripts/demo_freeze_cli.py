"""
Demo Freeze CLI Tool
Freeze/unfreeze demo metrics for consistent presentations
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from backend.database import SessionLocal
from backend.services.demo_metrics_service import DemoMetricsService
from backend.services.demo_freeze_service import DemoFreezeManager


def freeze_demo():
    """Freeze current metrics"""
    print("🔒 Freezing demo metrics...")
    
    db = SessionLocal()
    
    try:
        # Get current comprehensive metrics
        metrics_service = DemoMetricsService(db)
        metrics = metrics_service.get_comprehensive_demo_metrics()
        
        # Freeze them
        DemoFreezeManager.freeze_metrics(metrics)
        
        print("\n✅ Demo metrics frozen successfully!")
        print(f"📁 Cache file: {DemoFreezeManager.FREEZE_FILE}")
        print(f"🕒 Frozen at: {metrics['timestamp']}")
        
        print("\nFrozen metrics summary:")
        print(f"  - Total Wallets: {metrics['wallets']['total_wallets']}")
        print(f"  - Active Users: {metrics['wallets']['weekly_active_users']}")
        print(f"  - Success Rate: {metrics['transactions']['overall_success_rate']}%")
        print(f"  - Total Volume: {metrics['volume']['total_volume_algo']} ALGO")
        print(f"  - Fundraising: {metrics['fundraising']['total_raised_algo']} ALGO")
        print(f"  - Tickets: {metrics['tickets']['total_tickets_minted']}")
        
        print("\n🎯 To use frozen metrics:")
        print("  1. Set environment variable: DEMO_FREEZE=true")
        print("  2. Restart your FastAPI server")
        print("  3. All demo endpoints will serve these frozen metrics")
        
        print("\n💡 To unfreeze:")
        print("  python scripts/demo_freeze_cli.py unfreeze")
        
    except Exception as e:
        print(f"\n❌ Error freezing metrics: {str(e)}")
        raise
    
    finally:
        db.close()


def unfreeze_demo():
    """Unfreeze demo metrics"""
    print("🔓 Unfreezing demo metrics...")
    
    if DemoFreezeManager.unfreeze():
        print("\n✅ Demo metrics unfrozen!")
        print("📊 Endpoints will now serve live metrics")
        print("\n💡 Remember to unset DEMO_FREEZE environment variable")
    else:
        print("\n⚠️  No frozen metrics found")
        print("Demo was not frozen or cache file doesn't exist")


def status():
    """Show freeze status"""
    print("📊 Demo Freeze Status")
    print("="*60 + "\n")
    
    status = DemoFreezeManager.get_freeze_status()
    
    print(f"Environment Variable (DEMO_FREEZE): {os.getenv('DEMO_FREEZE', 'not set')}")
    print(f"Freeze Mode Active: {'✅ YES' if status['is_frozen'] else '❌ NO'}")
    print(f"Cache File Exists: {'✅ YES' if status['has_cache'] else '❌ NO'}")
    
    if status['has_cache']:
        print(f"\n📁 Cache Details:")
        print(f"  - Frozen At: {status['frozen_at']}")
        print(f"  - Cache Age: {status['cache_age_seconds']:.1f} seconds")
        print(f"  - File: {DemoFreezeManager.FREEZE_FILE}")
    else:
        print("\n⚠️  No cached metrics available")
        print("Run 'freeze' command to create cache")
    
    print("\n" + "="*60)


def main():
    """Main CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Demo Freeze Tool - Lock metrics for consistent presentations"
    )
    
    parser.add_argument(
        "command",
        choices=["freeze", "unfreeze", "status"],
        help="Command to execute"
    )
    
    args = parser.parse_args()
    
    if args.command == "freeze":
        freeze_demo()
    elif args.command == "unfreeze":
        unfreeze_demo()
    elif args.command == "status":
        status()


if __name__ == "__main__":
    main()
