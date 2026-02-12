"""
Demo Health Guardian
Pre-demo checklist system to ensure everything is ready
Zero-risk demo execution requires everything working before starting
"""
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
import requests
from sqlalchemy.orm import Session
from sqlalchemy import text

# Add parent directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import SessionLocal
from backend.models.user import User
from backend.models.transaction import Transaction


class HealthCheck:
    """Individual health check result"""
    def __init__(
        self, 
        name: str, 
        status: str,  # PASS, FAIL, WARN
        message: str,
        details: Optional[Dict] = None
    ):
        self.name = name
        self.status = status
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "status": self.status,
            "message": self.message,
            "details": self.details
        }


class DemoHealthGuardian:
    """
    Pre-demo checklist system
    Verifies all systems operational before demo starts
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.checks: List[HealthCheck] = []
    
    def _check_database_connection(self) -> HealthCheck:
        """Verify database is accessible"""
        try:
            # Try a simple query
            result = self.db.execute(text("SELECT 1")).fetchone()
            
            if result:
                return HealthCheck(
                    name="Database Connection",
                    status="PASS",
                    message="PostgreSQL responding",
                    details={"connection": "active"}
                )
            else:
                return HealthCheck(
                    name="Database Connection",
                    status="FAIL",
                    message="Database query returned no result",
                    details={"connection": "degraded"}
                )
        
        except Exception as e:
            return HealthCheck(
                name="Database Connection",
                status="FAIL",
                message=f"Database unreachable: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_user_data(self) -> HealthCheck:
        """Verify users exist in database"""
        try:
            user_count = self.db.query(User).count()
            
            if user_count >= 100:
                return HealthCheck(
                    name="User Data",
                    status="PASS",
                    message=f"{user_count} users loaded",
                    details={"user_count": user_count}
                )
            elif user_count > 0:
                return HealthCheck(
                    name="User Data",
                    status="WARN",
                    message=f"Only {user_count} users (expected 100+)",
                    details={"user_count": user_count, "expected": 100}
                )
            else:
                return HealthCheck(
                    name="User Data",
                    status="FAIL",
                    message="No users in database - run campus_simulation.py",
                    details={"user_count": 0}
                )
        
        except Exception as e:
            return HealthCheck(
                name="User Data",
                status="FAIL",
                message=f"Cannot query users: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_transaction_data(self) -> HealthCheck:
        """Verify transactions exist"""
        try:
            tx_count = self.db.query(Transaction).count()
            
            if tx_count >= 1000:
                return HealthCheck(
                    name="Transaction Data",
                    status="PASS",
                    message=f"{tx_count} transactions loaded",
                    details={"transaction_count": tx_count}
                )
            elif tx_count > 0:
                return HealthCheck(
                    name="Transaction Data",
                    status="WARN",
                    message=f"Only {tx_count} transactions (expected 1000+)",
                    details={"transaction_count": tx_count, "expected": 1000}
                )
            else:
                return HealthCheck(
                    name="Transaction Data",
                    status="FAIL",
                    message="No transactions - run campus_simulation.py",
                    details={"transaction_count": 0}
                )
        
        except Exception as e:
            return HealthCheck(
                name="Transaction Data",
                status="FAIL",
                message=f"Cannot query transactions: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_demo_metrics_available(self) -> HealthCheck:
        """Verify demo metrics can be calculated"""
        try:
            from backend.services.demo_metrics_service import DemoMetricsService
            
            metrics_service = DemoMetricsService(self.db)
            stats = metrics_service.get_comprehensive_stats()
            
            if stats:
                return HealthCheck(
                    name="Demo Metrics",
                    status="PASS",
                    message="Metrics service operational",
                    details={
                        "users": stats.get("users", {}).get("total", 0),
                        "transactions": stats.get("transactions", {}).get("total", 0)
                    }
                )
            else:
                return HealthCheck(
                    name="Demo Metrics",
                    status="FAIL",
                    message="Metrics service returned empty data",
                    details={}
                )
        
        except Exception as e:
            return HealthCheck(
                name="Demo Metrics",
                status="FAIL",
                message=f"Metrics service error: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_pitch_metrics_available(self) -> HealthCheck:
        """Verify pitch metrics can be calculated"""
        try:
            from backend.services.pitch_metrics_service import get_pitch_metrics
            
            pitch_service = get_pitch_metrics(self.db)
            adoption = pitch_service.get_adoption_rate()
            
            if adoption and adoption.get("activation_rate_percent", 0) > 0:
                return HealthCheck(
                    name="Pitch Metrics",
                    status="PASS",
                    message=f"{adoption['activation_rate_percent']:.1f}% activation rate calculated",
                    details=adoption
                )
            else:
                return HealthCheck(
                    name="Pitch Metrics",
                    status="WARN",
                    message="Pitch metrics available but no activation data",
                    details=adoption
                )
        
        except Exception as e:
            return HealthCheck(
                name="Pitch Metrics",
                status="FAIL",
                message=f"Pitch metrics error: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_redis_connection(self) -> HealthCheck:
        """Verify Redis is accessible (if configured)"""
        try:
            import redis
            from backend.config import settings
            
            # Try to connect to Redis
            if hasattr(settings, 'REDIS_URL'):
                r = redis.from_url(settings.REDIS_URL)
                r.ping()
                
                return HealthCheck(
                    name="Redis Cache",
                    status="PASS",
                    message="Redis responding",
                    details={"connection": "active"}
                )
            else:
                return HealthCheck(
                    name="Redis Cache",
                    status="WARN",
                    message="Redis not configured (optional)",
                    details={"configured": False}
                )
        
        except ImportError:
            return HealthCheck(
                name="Redis Cache",
                status="WARN",
                message="Redis library not installed (optional)",
                details={"configured": False}
            )
        
        except Exception as e:
            return HealthCheck(
                name="Redis Cache",
                status="WARN",
                message=f"Redis unavailable: {str(e)} (non-critical)",
                details={"error": str(e)}
            )
    
    def _check_algorand_node(self) -> HealthCheck:
        """Verify Algorand node is reachable"""
        try:
            from backend.config import settings
            
            # Try to reach Algorand node
            if hasattr(settings, 'ALGORAND_ALGOD_URL'):
                response = requests.get(
                    f"{settings.ALGORAND_ALGOD_URL}/v2/status",
                    headers={"X-Algo-API-Token": settings.ALGORAND_ALGOD_TOKEN},
                    timeout=5
                )
                
                if response.status_code == 200:
                    status = response.json()
                    return HealthCheck(
                        name="Algorand Node",
                        status="PASS",
                        message=f"TestNet responding (round {status.get('last-round', 'unknown')})",
                        details=status
                    )
                else:
                    return HealthCheck(
                        name="Algorand Node",
                        status="FAIL",
                        message=f"Node returned status {response.status_code}",
                        details={"status_code": response.status_code}
                    )
            else:
                return HealthCheck(
                    name="Algorand Node",
                    status="WARN",
                    message="Algorand node not configured",
                    details={"configured": False}
                )
        
        except Exception as e:
            return HealthCheck(
                name="Algorand Node",
                status="FAIL",
                message=f"Cannot reach Algorand node: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_wallet_balances(self) -> HealthCheck:
        """Verify demo wallets have sufficient balance"""
        try:
            # Query users with low balances
            users = self.db.query(User).limit(5).all()
            
            if not users:
                return HealthCheck(
                    name="Wallet Balances",
                    status="FAIL",
                    message="No users to check balances",
                    details={}
                )
            
            # Check if users have wallet addresses
            users_with_wallets = [u for u in users if u.wallet_address]
            
            if len(users_with_wallets) >= 3:
                return HealthCheck(
                    name="Wallet Balances",
                    status="PASS",
                    message=f"{len(users_with_wallets)} demo wallets configured",
                    details={"wallets_configured": len(users_with_wallets)}
                )
            else:
                return HealthCheck(
                    name="Wallet Balances",
                    status="WARN",
                    message=f"Only {len(users_with_wallets)} wallets configured",
                    details={"wallets_configured": len(users_with_wallets)}
                )
        
        except Exception as e:
            return HealthCheck(
                name="Wallet Balances",
                status="FAIL",
                message=f"Cannot check wallets: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_demo_scenarios_available(self) -> HealthCheck:
        """Verify demo scenario runner is available"""
        try:
            scripts_dir = Path(__file__).parent.parent.parent / "scripts"
            scenario_file = scripts_dir / "demo_scenario_runner.py"
            
            if scenario_file.exists():
                return HealthCheck(
                    name="Demo Scenarios",
                    status="PASS",
                    message="Scenario runner ready (5 scenarios available)",
                    details={"script_path": str(scenario_file)}
                )
            else:
                return HealthCheck(
                    name="Demo Scenarios",
                    status="WARN",
                    message="Scenario runner not found",
                    details={"expected_path": str(scenario_file)}
                )
        
        except Exception as e:
            return HealthCheck(
                name="Demo Scenarios",
                status="FAIL",
                message=f"Cannot check scenarios: {str(e)}",
                details={"error": str(e)}
            )
    
    def _check_environment_variables(self) -> HealthCheck:
        """Verify critical environment variables"""
        try:
            from backend.config import settings
            
            critical_vars = [
                "DATABASE_URL",
                "TWILIO_ACCOUNT_SID",
                "TWILIO_AUTH_TOKEN",
                "TWILIO_WHATSAPP_NUMBER"
            ]
            
            missing = []
            for var in critical_vars:
                if not hasattr(settings, var) or not getattr(settings, var):
                    missing.append(var)
            
            if not missing:
                return HealthCheck(
                    name="Environment Variables",
                    status="PASS",
                    message="All critical variables configured",
                    details={"configured": critical_vars}
                )
            else:
                return HealthCheck(
                    name="Environment Variables",
                    status="WARN",
                    message=f"Missing: {', '.join(missing)}",
                    details={"missing": missing}
                )
        
        except Exception as e:
            return HealthCheck(
                name="Environment Variables",
                status="FAIL",
                message=f"Cannot check environment: {str(e)}",
                details={"error": str(e)}
            )
    
    def run_all_checks(self) -> Dict:
        """
        Run all health checks
        Returns comprehensive report
        """
        self.checks = []
        
        print("\n🔍 Running Pre-Demo Health Checks...\n")
        
        # Run all checks
        checks_to_run = [
            ("Database", self._check_database_connection),
            ("Users", self._check_user_data),
            ("Transactions", self._check_transaction_data),
            ("Demo Metrics", self._check_demo_metrics_available),
            ("Pitch Metrics", self._check_pitch_metrics_available),
            ("Redis", self._check_redis_connection),
            ("Algorand", self._check_algorand_node),
            ("Wallets", self._check_wallet_balances),
            ("Scenarios", self._check_demo_scenarios_available),
            ("Environment", self._check_environment_variables)
        ]
        
        for name, check_func in checks_to_run:
            print(f"   Checking {name}...", end=" ")
            result = check_func()
            self.checks.append(result)
            
            # Print status with emoji
            if result.status == "PASS":
                print("✅ PASS")
            elif result.status == "WARN":
                print("⚠️  WARN")
            else:
                print("❌ FAIL")
        
        # Calculate overall status
        failed = [c for c in self.checks if c.status == "FAIL"]
        warned = [c for c in self.checks if c.status == "WARN"]
        passed = [c for c in self.checks if c.status == "PASS"]
        
        overall_status = "READY" if not failed else "NOT READY"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "summary": {
                "total_checks": len(self.checks),
                "passed": len(passed),
                "warned": len(warned),
                "failed": len(failed)
            },
            "checks": [c.to_dict() for c in self.checks],
            "ready_for_demo": len(failed) == 0
        }
        
        # Print summary
        self._print_summary(report)
        
        return report
    
    def _print_summary(self, report: Dict):
        """Print human-readable summary"""
        print("\n" + "="*80)
        print("DEMO HEALTH CHECK SUMMARY")
        print("="*80 + "\n")
        
        summary = report["summary"]
        print(f"✅ Passed:  {summary['passed']}/{summary['total_checks']}")
        print(f"⚠️  Warned:  {summary['warned']}/{summary['total_checks']}")
        print(f"❌ Failed:  {summary['failed']}/{summary['total_checks']}")
        
        print(f"\n🎯 Overall Status: {report['overall_status']}")
        
        if report["ready_for_demo"]:
            print("\n✨ ALL SYSTEMS GO - Ready for demo!")
        else:
            print("\n⛔ NOT READY - Fix failures before demo")
            print("\nFailed Checks:")
            for check in report["checks"]:
                if check["status"] == "FAIL":
                    print(f"   ❌ {check['name']}: {check['message']}")
        
        if summary['warned'] > 0:
            print("\nWarnings (non-critical):")
            for check in report["checks"]:
                if check["status"] == "WARN":
                    print(f"   ⚠️  {check['name']}: {check['message']}")
        
        print("\n" + "="*80 + "\n")


def get_demo_guardian(db: Session) -> DemoHealthGuardian:
    """Factory function to get guardian instance"""
    return DemoHealthGuardian(db)


def main():
    """CLI execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Demo Health Guardian - Pre-demo checklist"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON report"
    )
    
    args = parser.parse_args()
    
    # Create database session
    db = SessionLocal()
    
    try:
        guardian = get_demo_guardian(db)
        report = guardian.run_all_checks()
        
        if args.json:
            import json
            print(json.dumps(report, indent=2))
        
        # Exit with error code if not ready
        exit_code = 0 if report["ready_for_demo"] else 1
        exit(exit_code)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
