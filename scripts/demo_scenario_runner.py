"""
Demo Scenario Runner
Predefined demo flows for zero-risk execution
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Any
from datetime import datetime
import time


class DemoStep:
    """Single step in a demo scenario"""
    
    def __init__(
        self,
        step_number: int,
        action: str,
        command: str,
        expected_response: str,
        expected_blockchain_time: str,
        expected_metrics_update: str,
        notes: str = ""
    ):
        self.step_number = step_number
        self.action = action
        self.command = command
        self.expected_response = expected_response
        self.expected_blockchain_time = expected_blockchain_time
        self.expected_metrics_update = expected_metrics_update
        self.notes = notes
    
    def display(self):
        """Display step details"""
        print(f"\n{'='*80}")
        print(f"STEP {self.step_number}: {self.action}")
        print('='*80)
        
        print(f"\n📱 COMMAND TO SEND:")
        print(f"   {self.command}")
        
        print(f"\n✅ EXPECTED WHATSAPP RESPONSE:")
        print(f"{self.expected_response}")
        
        print(f"\n⏱️  EXPECTED BLOCKCHAIN TIME:")
        print(f"   {self.expected_blockchain_time}")
        
        print(f"\n📊 EXPECTED METRICS UPDATE:")
        print(f"   {self.expected_metrics_update}")
        
        if self.notes:
            print(f"\n💡 NOTES:")
            print(f"   {self.notes}")
        
        print(f"\n{'='*80}\n")


class DemoScenario:
    """Complete demo scenario with multiple steps"""
    
    def __init__(self, name: str, description: str, steps: List[DemoStep]):
        self.name = name
        self.description = description
        self.steps = steps
    
    def run(self, pause_between_steps: bool = True):
        """Execute demo scenario"""
        print("\n" + "🎬" * 40)
        print(f"DEMO SCENARIO: {self.name}")
        print("🎬" * 40)
        print(f"\n{self.description}\n")
        
        for step in self.steps:
            step.display()
            
            if pause_between_steps and step.step_number < len(self.steps):
                input("Press ENTER to continue to next step...")
        
        print("\n" + "✅" * 40)
        print(f"SCENARIO COMPLETE: {self.name}")
        print("✅" * 40 + "\n")


class DemoScenarioRunner:
    """
    Manages all predefined demo scenarios
    Zero-risk demo execution with step-by-step guidance
    """
    
    def __init__(self):
        self.scenarios = {
            1: self._create_onboarding_scenario(),
            2: self._create_payment_scenario(),
            3: self._create_bill_split_scenario(),
            4: self._create_nft_ticket_scenario(),
            5: self._create_fundraising_scenario()
        }
    
    def _create_onboarding_scenario(self) -> DemoScenario:
        """Flow 1: First user onboarding"""
        steps = [
            DemoStep(
                step_number=1,
                action="Send first message to bot",
                command="help",
                expected_response="""🏦 *AlgoChat Pay - Campus Wallet*

*Available Commands:*

💰 *Balance & Wallet*
• `balance` - Check your wallet balance

💸 *Payments*
• `pay 50 ALGO to +91XXXXXXXXXX` - Send ALGO
• `split 400 ALGO dinner with +91XXX +91YYY` - Split bill

🎫 *Event Tickets*
• `buy ticket TechFest` - Purchase event ticket (NFT)

Need help? Just type `help` anytime!""",
                expected_blockchain_time="N/A (no blockchain interaction)",
                expected_metrics_update="User engagement +1",
                notes="This shows the help menu. User is learning the bot interface."
            ),
            DemoStep(
                step_number=2,
                action="Check wallet balance",
                command="balance",
                expected_response="""💰 *Your Wallet Balance*

Address: ABCD...XYZ (truncated)
Balance: 100.00 ALGO

Your wallet is ready to use!""",
                expected_blockchain_time="~0.5s (Algorand node query)",
                expected_metrics_update="Active wallet check +1",
                notes="Wallet auto-created on first interaction. 100 ALGO testnet balance provided."
            ),
            DemoStep(
                step_number=3,
                action="View transaction history",
                command="history",
                expected_response="""📊 *Transaction History*

No transactions yet.

Start by sending a payment or buying tickets!""",
                expected_blockchain_time="~0.3s (database query)",
                expected_metrics_update="History views +1",
                notes="Empty history for new user. Ready to make first transaction."
            )
        ]
        
        return DemoScenario(
            name="First User Onboarding",
            description="Demonstrate how a new student sets up their wallet via WhatsApp",
            steps=steps
        )
    
    def _create_payment_scenario(self) -> DemoScenario:
        """Flow 2: Payment send"""
        steps = [
            DemoStep(
                step_number=1,
                action="Send payment command",
                command="pay 10 ALGO to +14155550123",
                expected_response="""⏳ *Payment Processing*

Sending 10 ALGO to +14155550123
Please wait while we confirm on blockchain...""",
                expected_blockchain_time="~4.5s (Algorand confirmation)",
                expected_metrics_update="Pending transactions +1",
                notes="Payment initiated. Algorand transaction submitted to network."
            ),
            DemoStep(
                step_number=2,
                action="Receive confirmation",
                command="N/A (automatic)",
                expected_response="""✅ *Payment Confirmed!*

Sent: 10 ALGO
To: +14155550123
Transaction ID: ABCD1234...
Time: 4.5 seconds

Your new balance: 90.00 ALGO""",
                expected_blockchain_time="4.5s average",
                expected_metrics_update="Confirmed transactions +1, Total volume +10 ALGO, Success rate updated",
                notes="Blockchain confirmed. Transaction immutable. User notified automatically."
            ),
            DemoStep(
                step_number=3,
                action="Verify in history",
                command="history",
                expected_response="""📊 *Transaction History*

1. ✅ Payment Sent
   Amount: 10 ALGO
   To: +14155550123
   Time: 2 minutes ago
   Status: Confirmed

Total: 1 transaction""",
                expected_blockchain_time="~0.3s (database query)",
                expected_metrics_update="History views +1",
                notes="Transaction now appears in history. Blockchain proof available."
            )
        ]
        
        return DemoScenario(
            name="Peer-to-Peer Payment",
            description="Send ALGO to another student for lunch",
            steps=steps
        )
    
    def _create_bill_split_scenario(self) -> DemoScenario:
        """Flow 3: Bill split"""
        steps = [
            DemoStep(
                step_number=1,
                action="Initiate bill split",
                command="split 40 ALGO dinner with +14155550123 +14155550124 +14155550125",
                expected_response="""💸 *Bill Split Initiated*

Total: 40 ALGO
Split 4 ways (including you)
Each pays: 10 ALGO

Participants:
• You (+14155550100)
• +14155550123
• +14155550124
• +14155550125

Processing group transaction...""",
                expected_blockchain_time="~4.5s (Algorand atomic transfer)",
                expected_metrics_update="Group transactions +1, Participants +4",
                notes="Algorand atomic transfer ensures all-or-nothing execution."
            ),
            DemoStep(
                step_number=2,
                action="Receive confirmation",
                command="N/A (automatic)",
                expected_response="""✅ *Bill Split Confirmed!*

Your share: 10 ALGO
Total bill: 40 ALGO
Split with: 3 others

All payments confirmed on blockchain.
Transaction ID: GRPTXN...

Your new balance: 80.00 ALGO""",
                expected_blockchain_time="4.5s average",
                expected_metrics_update="Confirmed group transactions +1, Volume +40 ALGO",
                notes="All 4 payments confirmed atomically. No one can back out after confirmation."
            )
        ]
        
        return DemoScenario(
            name="Bill Split",
            description="Split dinner bill with 3 friends using atomic transfer",
            steps=steps
        )
    
    def _create_nft_ticket_scenario(self) -> DemoScenario:
        """Flow 4: NFT ticket purchase"""
        steps = [
            DemoStep(
                step_number=1,
                action="Browse available tickets",
                command="my tickets",
                expected_response="""🎫 *Your Tickets*

No tickets yet.

Buy tickets using: `buy ticket EventName`""",
                expected_blockchain_time="~0.3s (database query)",
                expected_metrics_update="Ticket queries +1",
                notes="User has no tickets yet. Ready to purchase."
            ),
            DemoStep(
                step_number=2,
                action="Purchase NFT ticket",
                command="buy ticket TechFest 2026",
                expected_response="""⏳ *Minting NFT Ticket*

Event: TechFest 2026
Price: 8 ALGO

Creating your blockchain-secured ticket...""",
                expected_blockchain_time="~5.0s (NFT minting + smart contract)",
                expected_metrics_update="Pending tickets +1",
                notes="NFT being minted on Algorand. Smart contract ensures authenticity."
            ),
            DemoStep(
                step_number=3,
                action="Receive NFT ticket",
                command="N/A (automatic)",
                expected_response="""✅ *Ticket Minted!*

Event: TechFest 2026
Ticket #: TIX-TF2026-00312
NFT Asset ID: 1234567
Price: 8 ALGO

Your ticket is blockchain-secured and fraud-proof.
Show this at entry for verification.

Your new balance: 72.00 ALGO""",
                expected_blockchain_time="5.0s average",
                expected_metrics_update="Tickets minted +1, Ticket revenue +8 ALGO",
                notes="NFT ticket now owned by user. Cannot be counterfeited or duplicated."
            ),
            DemoStep(
                step_number=4,
                action="View owned tickets",
                command="my tickets",
                expected_response="""🎫 *Your Tickets*

1. TechFest 2026
   Ticket #: TIX-TF2026-00312
   Status: Valid ✅
   Date: May 15, 2026
   NFT Asset: 1234567

Total: 1 ticket""",
                expected_blockchain_time="~0.3s (database query)",
                expected_metrics_update="Ticket views +1",
                notes="User can view their NFT tickets anytime. Ready for event entry."
            ),
            DemoStep(
                step_number=5,
                action="Verify ticket authenticity",
                command="verify ticket TIX-TF2026-00312",
                expected_response="""✅ *Ticket Verified*

Ticket #: TIX-TF2026-00312
Event: TechFest 2026
Status: Valid and Unused
Owner: +14155550100
NFT Asset: 1234567

Blockchain verification: PASSED ✅

This ticket is authentic and has not been used.""",
                expected_blockchain_time="~1.0s (blockchain verification)",
                expected_metrics_update="Verifications +1",
                notes="Anyone can verify ticket authenticity. Fraud detection at entry."
            )
        ]
        
        return DemoScenario(
            name="NFT Event Ticket Purchase",
            description="Buy and verify blockchain-secured event ticket",
            steps=steps
        )
    
    def _create_fundraising_scenario(self) -> DemoScenario:
        """Flow 5: Fundraising pool"""
        steps = [
            DemoStep(
                step_number=1,
                action="Create fundraising campaign",
                command="create fund Library Renovation goal 500 ALGO",
                expected_response="""❤️ *Fundraising Campaign Created*

Campaign: Library Renovation
Goal: 500 ALGO
Campaign ID: 3

Share this ID with contributors.
Track progress: `view fund 3`""",
                expected_blockchain_time="~0.5s (database + smart contract setup)",
                expected_metrics_update="Active campaigns +1",
                notes="Campaign created. Ready to accept contributions."
            ),
            DemoStep(
                step_number=2,
                action="View campaign details",
                command="view fund 3",
                expected_response="""❤️ *Fundraising Campaign*

Campaign: Library Renovation
Campaign ID: 3

Goal: 500 ALGO
Raised: 0 ALGO (0%)
Contributors: 0

Status: Active 🟢

Contribute: `contribute 50 ALGO to fund 3`""",
                expected_blockchain_time="~0.3s (database query)",
                expected_metrics_update="Campaign views +1",
                notes="Campaign just created. Zero contributions so far."
            ),
            DemoStep(
                step_number=3,
                action="Make contribution",
                command="contribute 25 ALGO to fund 3",
                expected_response="""⏳ *Processing Contribution*

Amount: 25 ALGO
Campaign: Library Renovation
Campaign ID: 3

Sending to fundraising smart contract...""",
                expected_blockchain_time="~4.5s (Algorand confirmation)",
                expected_metrics_update="Pending contributions +1",
                notes="Contribution submitted to smart contract. Transparent and traceable."
            ),
            DemoStep(
                step_number=4,
                action="Receive contribution confirmation",
                command="N/A (automatic)",
                expected_response="""✅ *Contribution Confirmed!*

Amount: 25 ALGO
Campaign: Library Renovation
Transaction ID: FUND...

Thank you for supporting campus causes!

New campaign progress: 25/500 ALGO (5%)

Your new balance: 47.00 ALGO""",
                expected_blockchain_time="4.5s average",
                expected_metrics_update="Confirmed contributions +1, Fundraising volume +25 ALGO",
                notes="Contribution recorded on blockchain. Campaign progress updated."
            ),
            DemoStep(
                step_number=5,
                action="Check updated campaign",
                command="view fund 3",
                expected_response="""❤️ *Fundraising Campaign*

Campaign: Library Renovation
Campaign ID: 3

Goal: 500 ALGO
Raised: 25 ALGO (5%)
Contributors: 1

Status: Active 🟢

Recent contribution: 25 ALGO (you)

Contribute: `contribute 50 ALGO to fund 3`""",
                expected_blockchain_time="~0.3s (database query)",
                expected_metrics_update="Campaign views +1",
                notes="Campaign progress visible to all. Transparent fundraising."
            )
        ]
        
        return DemoScenario(
            name="Fundraising Campaign",
            description="Create and contribute to campus fundraising pool",
            steps=steps
        )
    
    def list_scenarios(self):
        """List all available scenarios"""
        print("\n" + "📋" * 40)
        print("AVAILABLE DEMO SCENARIOS")
        print("📋" * 40 + "\n")
        
        for num, scenario in self.scenarios.items():
            print(f"{num}. {scenario.name}")
            print(f"   {scenario.description}")
            print(f"   Steps: {len(scenario.steps)}")
            print()
    
    def run_scenario(self, scenario_number: int, pause: bool = True):
        """Run specific scenario"""
        if scenario_number not in self.scenarios:
            print(f"❌ Scenario {scenario_number} not found")
            return
        
        scenario = self.scenarios[scenario_number]
        scenario.run(pause_between_steps=pause)
    
    def run_all_scenarios(self, pause: bool = False):
        """Run all scenarios in sequence"""
        print("\n" + "🎬" * 40)
        print("RUNNING ALL DEMO SCENARIOS")
        print("🎬" * 40 + "\n")
        
        for num in sorted(self.scenarios.keys()):
            self.run_scenario(num, pause=pause)
            if pause and num < max(self.scenarios.keys()):
                input("\nPress ENTER to continue to next scenario...")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Demo Scenario Runner - Zero-risk demo execution"
    )
    
    parser.add_argument(
        "action",
        nargs='?',
        choices=["list", "run", "all"],
        default="list",
        help="Action: list scenarios, run specific scenario, or run all"
    )
    
    parser.add_argument(
        "--scenario",
        type=int,
        help="Scenario number to run (1-5)"
    )
    
    parser.add_argument(
        "--no-pause",
        action="store_true",
        help="Run without pausing between steps"
    )
    
    args = parser.parse_args()
    
    runner = DemoScenarioRunner()
    
    if args.action == "list":
        runner.list_scenarios()
    
    elif args.action == "run":
        if not args.scenario:
            print("❌ Please specify --scenario NUMBER")
            runner.list_scenarios()
            return
        
        runner.run_scenario(args.scenario, pause=not args.no_pause)
    
    elif args.action == "all":
        runner.run_all_scenarios(pause=not args.no_pause)


if __name__ == "__main__":
    main()
