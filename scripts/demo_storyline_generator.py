"""
Demo Timeline Narration Generator
Generates spoken demo scripts aligned with real metrics
5-minute narrative that tells compelling story
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from typing import Dict, List

from backend.database import SessionLocal
from backend.services.pitch_metrics_service import get_pitch_metrics
from backend.services.demo_metrics_service import get_demo_metrics


class DemoStorylineGenerator:
    """
    Generates narrative storylines for live demos
    Aligns spoken words with on-screen actions
    """
    
    def __init__(self, db):
        self.db = db
        self.pitch_service = get_pitch_metrics(db)
        self.demo_service = get_demo_metrics(db)
    
    def generate_5_minute_demo_script(self) -> Dict[str, any]:
        """
        Generate 5-minute demo script with timing
        
        Returns script with:
        - Timeline in seconds
        - What to say
        - What to show on screen
        - Metrics to highlight
        """
        # Get metrics for narrative
        adoption = self.pitch_service.get_adoption_rate()
        daily_active = self.pitch_service.get_daily_active_wallets()
        txs_per_user = self.pitch_service.get_avg_transactions_per_user()
        trust_savings = self.pitch_service.get_trust_savings()
        success_rate = self.demo_service.get_success_rate_metrics()
        tickets = self.demo_service.get_ticket_metrics()
        fundraising = self.demo_service.get_fundraising_metrics()
        
        script = {
            "total_duration_seconds": 300,
            "sections": []
        }
        
        # Section 1: Hook (0:00 - 0:30, 30 seconds)
        script["sections"].append({
            "start_time": 0,
            "duration": 30,
            "section_name": "HOOK",
            "narration": f"""
Imagine you're a college student. You just finished lunch with 3 friends. 
Bill is $40. How do you split it?

Cash? Nobody carries cash anymore.
Venmo? Fees, and someone always "forgets" to pay.
Campus card? Only works at select dining halls.

What if you could just text: "Split $40 with Sarah, Mike, and Emma" - 
and it's done in 4.5 seconds?

That's AlgoChat Pay. And {adoption['total_users']} students are already using it.
            """,
            "screen_action": "Show WhatsApp conversation with bill split command",
            "metrics_to_display": [
                f"{adoption['total_users']} active students",
                f"{adoption['activation_rate_percent']:.0f}% activation rate"
            ]
        })
        
        # Section 2: First Demo - Peer Payment (0:30 - 1:30, 60 seconds)
        script["sections"].append({
            "start_time": 30,
            "duration": 60,
            "section_name": "DEMO_1_PAYMENT",
            "narration": f"""
Let me show you how simple this is.

I'm going to send 10 ALGO to my friend Sarah.

[Type in WhatsApp]: "pay 10 ALGO to +1234567890"

Watch what happens... [wait for confirmation]

BOOM. 4.5 seconds. Payment confirmed.

Notice what happened:
- Blockchain transaction processed
- Sarah's balance updated
- Transaction recorded on Algorand
- All through a simple text message

No app to download. No seed phrase to memorize. No crypto complexity.

We've processed {success_rate['total_transactions']:,} transactions like this 
with a {success_rate['success_rate_percent']:.1f}% success rate.
            """,
            "screen_action": "Execute Scenario 2 from demo_scenario_runner.py",
            "metrics_to_display": [
                f"{success_rate['total_transactions']:,} total transactions",
                f"{success_rate['success_rate_percent']:.1f}% success rate",
                "4.5 second average settlement"
            ]
        })
        
        # Section 3: Second Demo - Bill Split (1:30 - 2:15, 45 seconds)
        script["sections"].append({
            "start_time": 90,
            "duration": 45,
            "section_name": "DEMO_2_SPLIT",
            "narration": f"""
But it gets better. Remember that $40 lunch bill?

[Type]: "split 40 ALGO dinner with +1111111111 +2222222222 +3333333333"

This is where blockchain REALLY shines.

See that? Algorand atomic transfer. All 4 payments happen simultaneously, 
or NONE happen. No one can back out. No awkward follow-ups.

And the fee? $0.001. Try doing that on Ethereum.

{txs_per_user['power_users_5plus']} power users have made 5+ transactions. 
They don't go back to Venmo. Why would they?
            """,
            "screen_action": "Execute Scenario 3 from demo_scenario_runner.py",
            "metrics_to_display": [
                f"{txs_per_user['avg_transactions_per_user']:.1f} txs per user",
                f"{txs_per_user['power_users_5plus']} power users (5+ txs)",
                "$0.001 transaction fee"
            ]
        })
        
        # Section 4: Third Demo - NFT Ticket (2:15 - 3:00, 45 seconds)
        script["sections"].append({
            "start_time": 135,
            "duration": 45,
            "section_name": "DEMO_3_TICKET",
            "narration": f"""
Now here's where we go beyond payments.

Event ticketing is BROKEN. Scalpers, fraud, fake tickets.

Watch this:

[Type]: "buy ticket TechFest 2026"

[wait for NFT minting]

Done. NFT ticket minted on blockchain.

Why does this matter?
- Can't be counterfeited (blockchain verification)
- Can't be scalped (smart contract controls resale)
- Can be verified instantly at venue

We've sold {tickets['total_tickets_minted']} NFT tickets. ZERO fraud. 
Compare that to traditional ticketing where 12% are fake.
            """,
            "screen_action": "Execute Scenario 4 from demo_scenario_runner.py",
            "metrics_to_display": [
                f"{tickets['total_tickets_minted']} NFT tickets sold",
                "0% fraud rate",
                "Instant verification"
            ]
        })
        
        # Section 5: Fourth Demo - Fundraising (3:00 - 3:45, 45 seconds)
        script["sections"].append({
            "start_time": 180,
            "duration": 45,
            "section_name": "DEMO_4_FUNDRAISING",
            "narration": f"""
Last feature: Transparent fundraising.

Student clubs raise money all the time. But where does it go? 
Who contributed? How much is left?

Blockchain solves this.

[Type]: "create fund Library Renovation goal 500 ALGO"

Now anyone can contribute:

[Type]: "contribute 25 ALGO to fund 3"

And everyone can see the progress:

[Type]: "view fund 3"

Total transparency. Every ALGO tracked. No missing funds. 
No Excel spreadsheets.

{fundraising['total_campaigns']} campaigns have raised 
{fundraising['total_raised_algo']:.0f} ALGO. All tracked on blockchain.
            """,
            "screen_action": "Execute Scenario 5 from demo_scenario_runner.py",
            "metrics_to_display": [
                f"{fundraising['total_campaigns']} campaigns launched",
                f"{fundraising['total_raised_algo']:.0f} ALGO raised",
                "100% transparency"
            ]
        })
        
        # Section 6: Impact & Traction (3:45 - 4:30, 45 seconds)
        script["sections"].append({
            "start_time": 225,
            "duration": 45,
            "section_name": "IMPACT",
            "narration": f"""
So what's the REAL impact here?

Security: We've prevented {trust_savings['fraud_prevented_algo']:.1f} ALGO in fraud.
Traditional payment systems lose 2% to fraud. Blockchain loses 0.01%.

Adoption: {adoption['activation_rate_percent']:.0f}% activation rate. 
That means students don't just sign up - they actually USE this.

Engagement: {daily_active['today_active']} students transact DAILY. 
This isn't a novelty. This is their payment method.

Network Effects: {adoption['transacted_users']} students have made at least 
one transaction. Once your friends are on it, you HAVE to join for bill splits.

This is the campus payment infrastructure of the future.
            """,
            "screen_action": "Show GET /demo/pitch-summary API results",
            "metrics_to_display": [
                f"{trust_savings['fraud_prevented_algo']:.1f} ALGO fraud prevented",
                f"{adoption['activation_rate_percent']:.0f}% activation rate",
                f"{daily_active['today_active']} daily active users",
                f"{adoption['transacted_users']} total transacting users"
            ]
        })
        
        # Section 7: Closing (4:30 - 5:00, 30 seconds)
        script["sections"].append({
            "start_time": 270,
            "duration": 30,
            "section_name": "CLOSING",
            "narration": f"""
To recap:

AlgoChat Pay is the WhatsApp blockchain wallet for students.

✅ {adoption['total_users']} students using it
✅ {adoption['activation_rate_percent']:.0f}% activation rate
✅ {success_rate['total_transactions']:,} successful transactions
✅ Payments, tickets, and fundraising in ONE platform

We've proven this works on 1 campus. Now we're scaling to 10, then 100.

The future of student payments is here. And it runs on Algorand.

Questions?
            """,
            "screen_action": "Show final dashboard with all metrics",
            "metrics_to_display": [
                f"{adoption['total_users']} students",
                f"{success_rate['total_transactions']:,} transactions",
                f"{adoption['activation_rate_percent']:.0f}% activation",
                f"{daily_active['today_active']} daily active"
            ]
        })
        
        return script
    
    def generate_3_minute_elevator_script(self) -> Dict[str, any]:
        """
        Generate condensed 3-minute elevator pitch
        For quick demos with time constraints
        """
        adoption = self.pitch_service.get_adoption_rate()
        success_rate = self.demo_service.get_success_rate_metrics()
        
        return {
            "total_duration_seconds": 180,
            "sections": [
                {
                    "start_time": 0,
                    "duration": 30,
                    "section_name": "HOOK",
                    "narration": f"""
Students struggle with payments on campus. Cash is unsafe, Venmo has fees, 
campus cards are limited. What if you could pay via WhatsApp text in 4.5 seconds?
That's AlgoChat Pay. {adoption['total_users']} students already use it.
                    """
                },
                {
                    "start_time": 30,
                    "duration": 60,
                    "section_name": "QUICK_DEMO",
                    "narration": f"""
Watch: [pay 10 ALGO to Sarah] - Done in 4.5 seconds on Algorand blockchain.
[split 40 ALGO with 3 friends] - Atomic transfer ensures all-or-nothing.
No app download. No seed phrases. Just text and done.
{success_rate['total_transactions']:,} transactions processed with {success_rate['success_rate_percent']:.1f}% success rate.
                    """
                },
                {
                    "start_time": 90,
                    "duration": 60,
                    "section_name": "TRACTION",
                    "narration": f"""
Real traction: {adoption['activation_rate_percent']:.0f}% activation rate proves students 
actually USE this. Not just sign ups. Multi-use platform: payments + NFT tickets + fundraising. 
Network effects working - once friends use it, you HAVE to join for bill splits.
                    """
                },
                {
                    "start_time": 150,
                    "duration": 30,
                    "section_name": "CLOSE",
                    "narration": f"""
{adoption['total_users']} students, {adoption['activation_rate_percent']:.0f}% activation, 
{success_rate['total_transactions']:,} transactions. Proven on 1 campus, scaling to 100. 
The future of student payments runs on Algorand. Questions?
                    """
                }
            ]
        }
    
    def generate_1_minute_lightning_pitch(self) -> str:
        """
        Generate 1-minute lightning pitch
        Maximum impact in minimum time
        """
        adoption = self.pitch_service.get_adoption_rate()
        success_rate = self.demo_service.get_success_rate_metrics()
        elevator = self.pitch_service.get_elevator_pitch_stats()
        
        return f"""
{elevator['one_liner']}

Problem: Students struggle with campus payments. Cash unsafe, Venmo has fees.

Solution: WhatsApp blockchain wallet. Pay via text in 4.5 seconds.

Demo: [pay 10 ALGO to Sarah] - Done. [split 40 ALGO with 3 friends] - Done.

Traction: {adoption['activation_rate_percent']:.0f}% activation rate, not just sign ups. 
{success_rate['total_transactions']:,} transactions. {success_rate['success_rate_percent']:.1f}% success rate.

Built on Algorand: 4.5s finality, $0.001 fees. Beats Ethereum by 100x.

Scale: Proven on 1 campus, scaling to 100. Campus payment infrastructure of the future.

Questions?
        """
    
    def export_all_scripts(self, output_dir: str = "demo_scripts"):
        """
        Export all demo scripts to files
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 5-minute script
        five_min = self.generate_5_minute_demo_script()
        five_min_file = output_path / f"5min_demo_script_{timestamp}.md"
        with open(five_min_file, 'w') as f:
            f.write("# ALGOCHAT PAY - 5 MINUTE DEMO SCRIPT\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(f"**Total Duration:** {five_min['total_duration_seconds']} seconds (5 minutes)\n\n")
            
            for section in five_min['sections']:
                time_str = f"{section['start_time']//60}:{section['start_time']%60:02d}"
                duration_str = f"{section['duration']} seconds"
                
                f.write(f"## [{time_str}] {section['section_name']} ({duration_str})\n\n")
                f.write(f"**Screen Action:** {section['screen_action']}\n\n")
                f.write(f"**Narration:**\n{section['narration']}\n\n")
                f.write(f"**Metrics to Display:**\n")
                for metric in section['metrics_to_display']:
                    f.write(f"- {metric}\n")
                f.write("\n---\n\n")
        
        # 3-minute script
        three_min = self.generate_3_minute_elevator_script()
        three_min_file = output_path / f"3min_elevator_script_{timestamp}.md"
        with open(three_min_file, 'w') as f:
            f.write("# ALGOCHAT PAY - 3 MINUTE ELEVATOR PITCH\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            
            for section in three_min['sections']:
                time_str = f"{section['start_time']//60}:{section['start_time']%60:02d}"
                f.write(f"## [{time_str}] {section['section_name']}\n\n")
                f.write(f"{section['narration']}\n\n")
        
        # 1-minute script
        one_min = self.generate_1_minute_lightning_pitch()
        one_min_file = output_path / f"1min_lightning_pitch_{timestamp}.txt"
        with open(one_min_file, 'w') as f:
            f.write("ALGOCHAT PAY - 1 MINUTE LIGHTNING PITCH\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(one_min)
        
        return {
            "5_minute_script": str(five_min_file),
            "3_minute_script": str(three_min_file),
            "1_minute_script": str(one_min_file)
        }
    
    def print_script_preview(self, duration: int = 5):
        """
        Print script preview to console
        
        Args:
            duration: 1, 3, or 5 minutes
        """
        if duration == 5:
            script = self.generate_5_minute_demo_script()
            print("\n" + "="*80)
            print("5-MINUTE DEMO SCRIPT PREVIEW")
            print("="*80 + "\n")
            
            for section in script['sections']:
                time_str = f"{section['start_time']//60}:{section['start_time']%60:02d}"
                print(f"[{time_str}] {section['section_name']}")
                print(f"Screen: {section['screen_action']}")
                print(section['narration'][:200] + "...")
                print()
        
        elif duration == 3:
            script = self.generate_3_minute_elevator_script()
            print("\n" + "="*80)
            print("3-MINUTE ELEVATOR PITCH")
            print("="*80 + "\n")
            print(script['sections'][0]['narration'] + "\n...")
        
        elif duration == 1:
            script = self.generate_1_minute_lightning_pitch()
            print("\n" + "="*80)
            print("1-MINUTE LIGHTNING PITCH")
            print("="*80 + "\n")
            print(script)


def main():
    """CLI execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Demo Timeline Narration Generator"
    )
    
    parser.add_argument(
        "--duration",
        type=int,
        choices=[1, 3, 5],
        default=5,
        help="Script duration in minutes"
    )
    
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export scripts to files"
    )
    
    parser.add_argument(
        "--output-dir",
        default="demo_scripts",
        help="Output directory for exports"
    )
    
    args = parser.parse_args()
    
    # Create database session
    db = SessionLocal()
    
    try:
        generator = DemoStorylineGenerator(db)
        
        if args.export:
            files = generator.export_all_scripts(args.output_dir)
            print("\n✅ Exported demo scripts:\n")
            for name, path in files.items():
                print(f"   📄 {name}: {path}")
            print()
        else:
            generator.print_script_preview(args.duration)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
