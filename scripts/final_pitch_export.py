"""
Final Pitch Stats Export
Export presentation-ready metrics for hackathon pitch deck
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from typing import Dict, List
import json

from backend.database import SessionLocal
from backend.services.pitch_metrics_service import get_pitch_metrics
from backend.services.demo_metrics_service import get_demo_metrics


class FinalPitchExporter:
    """
    Exports comprehensive pitch-ready statistics
    Formats for slides, speaker notes, and handouts
    """
    
    def __init__(self, db):
        self.db = db
        self.pitch_service = get_pitch_metrics(db)
        self.demo_service = get_demo_metrics(db)
        self.timestamp = datetime.now()
    
    def export_slide_bullets(self) -> Dict[str, List[str]]:
        """
        Export bullet points ready for pitch slides
        Organized by slide topic
        """
        # Get all metrics
        adoption = self.pitch_service.get_adoption_rate()
        daily_active = self.pitch_service.get_daily_active_wallets()
        txs_per_user = self.pitch_service.get_avg_transactions_per_user()
        campus_coverage = self.pitch_service.get_campus_coverage()
        trust_savings = self.pitch_service.get_trust_savings()
        impact_statements = self.pitch_service.get_judge_impact_statements()
        
        # Additional demo metrics
        success_rate = self.demo_service.get_success_rate_metrics()
        settlement_time = self.demo_service.get_average_settlement_time()
        tickets = self.demo_service.get_ticket_metrics()
        fundraising = self.demo_service.get_fundraising_metrics()
        
        return {
            "PROBLEM_SLIDE": [
                "Students struggle with peer payments on campus",
                "Cash is unsafe, Venmo has fees, campus card is limited",
                "No solution for event ticketing + fundraising + payments"
            ],
            
            "SOLUTION_SLIDE": [
                "WhatsApp-based blockchain wallet for students",
                "Zero-friction: No app download, no seed phrases",
                "Multi-use: Payments + NFT tickets + fundraising"
            ],
            
            "TECHNOLOGY_SLIDE": [
                "Built on Algorand blockchain for speed + security",
                f"4.5 second finality vs 12+ minutes (Ethereum)",
                "$0.001 transaction fee vs $5-50 (Ethereum)",
                "PyTeal smart contracts for bill splits + fundraising"
            ],
            
            "TRACTION_SLIDE": [
                f"✅ {adoption['total_users']} students already using the platform",
                f"✅ {adoption['activation_rate_percent']:.0f}% activation rate (students actually transact)",
                f"✅ {daily_active['today_active']} daily active users (consistent engagement)",
                f"✅ {txs_per_user['avg_transactions_per_user']:.1f} transactions per user (high usage)",
                f"✅ {campus_coverage['coverage_percent']:.0f}% campus penetration (network effects)"
            ],
            
            "METRICS_SLIDE": [
                f"Total Transactions: {success_rate['total_transactions']:,}",
                f"Success Rate: {success_rate['success_rate_percent']:.1f}%",
                f"Average Settlement: {settlement_time['average_seconds']:.1f} seconds",
                f"NFT Tickets Sold: {tickets['total_tickets_minted']:,}",
                f"Funds Raised: {fundraising['total_raised_algo']:.0f} ALGO"
            ],
            
            "IMPACT_SLIDE": [
                f"🔒 {trust_savings['fraud_prevented_algo']:.1f} ALGO fraud prevented",
                f"💰 ${trust_savings['dispute_resolution_savings_usd']:.0f} dispute resolution savings",
                f"⚡ {txs_per_user['power_users_5plus']} power users (5+ transactions)",
                f"🎟️ {tickets['total_tickets_minted']} tickets sold without scalping",
                f"🤝 {fundraising['total_campaigns']} fundraising campaigns launched"
            ],
            
            "BUSINESS_MODEL_SLIDE": [
                "Platform fee: 0.5% per transaction",
                "Merchant services for campus vendors",
                "Premium features ($2/month)",
                "Anonymous data insights for campus businesses"
            ],
            
            "COMPETITIVE_ADVANTAGE_SLIDE": [
                "Network effects: 77% of campus = winner-take-all",
                "WhatsApp integration = no app download barrier",
                "Multi-use platform = high switching cost",
                "Blockchain security = trust + transparency"
            ],
            
            "MARKET_SIZE_SLIDE": [
                "4,000+ universities in US",
                "20 million college students",
                "$200B+ annual student spending",
                "Target: 1% penetration = $2B opportunity"
            ],
            
            "GO_TO_MARKET_SLIDE": [
                "Campus-by-campus expansion model",
                "Student ambassadors + viral WhatsApp sharing",
                "University partnerships for official endorsement",
                "Target: 100 campuses in 18 months"
            ],
            
            "CLOSING_SLIDE": [
                f"{adoption['total_users']} students, {adoption['activation_rate_percent']:.0f}% activation",
                f"{daily_active['today_active']} daily active users",
                f"{success_rate['total_transactions']:,} transactions processed",
                "The future of student payments is here 🚀"
            ]
        }
    
    def export_speaker_notes(self) -> Dict[str, str]:
        """
        Export detailed speaker notes for each slide
        What to say during pitch
        """
        adoption = self.pitch_service.get_adoption_rate()
        impact_statements = self.pitch_service.get_judge_impact_statements()
        
        return {
            "OPENING": """
Hi judges, I'm here to show you AlgoChat Pay - the WhatsApp-based blockchain wallet 
that's transforming how students handle money on campus. We've already onboarded 
{users} students with a {activation}% activation rate, proving students don't just 
sign up - they actually use this.
""".format(
                users=adoption['total_users'],
                activation=f"{adoption['activation_rate_percent']:.0f}"
            ),
            
            "PROBLEM": """
Let me set the context. Students today struggle with three payment pain points:
1. Cash is unsafe - nobody wants to walk around campus with $100 cash
2. Venmo has fees and chargebacks cause disputes
3. Campus cards only work at select locations

But the bigger problem is FRAGMENTATION. Students need separate solutions for:
- Peer payments
- Event tickets  
- Club fundraising

What if one platform could do all three?
""",
            
            "SOLUTION": """
That's AlgoChat Pay. Here's how it works:
1. Students text a WhatsApp number
2. Instant blockchain wallet created
3. Pay friends, buy tickets, donate to clubs - all via text

No app download. No seed phrases. No crypto complexity.
Just: "Pay 10 ALGO to Sarah" - done in 4.5 seconds.
""",
            
            "TECHNOLOGY": """
We built this on Algorand blockchain for three reasons:

Speed: 4.5 second finality vs 12+ minutes on Ethereum. Students can't wait 15 minutes 
for lunch payment confirmation.

Cost: $0.001 per transaction vs $5-50 on Ethereum. Gas fees can't exceed the payment amount.

Smart Contracts: Our PyTeal contracts handle bill splitting (atomic transfers ensure 
all-or-nothing), fundraising (transparent goal tracking), and NFT tickets (prevents scalping).

We chose Algorand because it's built for payments, not DeFi speculation.
""",
            
            "TRACTION": """
Now here's the key - we have REAL traction:
- {users} students using it
- {activation}% activation rate means students actually transact, not just sign up
- {daily} students use it DAILY - this is their go-to payment method
- {txs_per_user} transactions per user proves high engagement
- {coverage}% campus penetration means network effects are working

{traction_statement}
""".format(
                users=adoption['total_users'],
                activation=f"{adoption['activation_rate_percent']:.0f}",
                daily=self.pitch_service.get_daily_active_wallets()['today_active'],
                txs_per_user=f"{self.pitch_service.get_avg_transactions_per_user()['avg_transactions_per_user']:.1f}",
                coverage=f"{self.pitch_service.get_campus_coverage()['coverage_percent']:.0f}",
                traction_statement=impact_statements['adoption_proof']
            ),
            
            "IMPACT": """
Let me show you the REAL impact:

Security: We've prevented {fraud} ALGO in fraud through blockchain immutability. 
Every transaction is traceable - no chargebacks, no disputes.

Efficiency: {tickets} NFT tickets sold without scalping or fraud. Students verify 
authenticity on blockchain in seconds.

Community: {campaigns} fundraising campaigns with transparent goal tracking. 
Donors see exactly where money goes.

{trust_statement}
""".format(
                fraud=f"{self.pitch_service.get_trust_savings()['fraud_prevented_algo']:.1f}",
                tickets=self.demo_service.get_ticket_metrics()['total_tickets_minted'],
                campaigns=self.demo_service.get_fundraising_metrics()['total_campaigns'],
                trust_statement=impact_statements['security_savings']
            ),
            
            "BUSINESS_MODEL": """
How do we make money? Simple:

Primary: 0.5% platform fee per transaction. That's WAY less than credit cards (2-3%) 
or even Stripe (2.9%). At scale - 50,000 students doing 2 transactions daily - that's 
$500K/year revenue.

Secondary: Merchant services for campus vendors, premium features, and anonymous 
data insights sold to campus businesses.

We're not guessing. The fintech model works. Stripe does $12B revenue on transaction fees.
""",
            
            "COMPETITIVE_ADVANTAGE": """
Why can't others copy us?

Network Effects: Once you have 77% of campus using it, bill splitting only works with us. 
Winner-take-all market.

Campus Partnerships: We integrate with university systems - student ID verification, 
official event ticketing. That partnership moat is hard to replicate.

Multi-Use Lock-In: Students use us for payments AND tickets AND fundraising. 
Switching cost is high.

Think Facebook - they weren't first social network, but network effects made them dominant.
""",
            
            "ASK": """
We're raising $500K to expand from 1 campus to 10 campuses in next 6 months.

With this funding:
- Hire 10 campus ambassadors
- Build university partnership pipeline  
- Scale infrastructure for 5,000+ students
- Launch merchant integration SDK

We've proven the model works on 1 campus. Now we're ready to replicate it nationally.

Who's ready to back the future of student payments?
"""
        }
    
    def export_one_pagers(self) -> Dict[str, str]:
        """
        Export one-page summaries for different audiences
        """
        adoption = self.pitch_service.get_adoption_rate()
        success_rate = self.demo_service.get_success_rate_metrics()
        trust_savings = self.pitch_service.get_trust_savings()
        
        judge_one_pager = f"""
ALGOCHAT PAY - HACKATHON PITCH ONE-PAGER
Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M')}

PROBLEM:
Students need separate apps for payments, event tickets, and fundraising.
Cash unsafe, Venmo has fees, campus cards limited.

SOLUTION:
WhatsApp-based blockchain wallet. Pay friends, buy NFT tickets, donate to clubs - all via text.
No app download. No seed phrases. Custodial security.

TECHNOLOGY:
- Algorand blockchain (4.5s finality, $0.001 fees)
- PyTeal smart contracts (bill splits, fundraising, NFT tickets)
- WhatsApp API integration (zero friction onboarding)

TRACTION:
✅ {adoption['total_users']} students using platform
✅ {adoption['activation_rate_percent']:.0f}% activation rate (students actually transact)
✅ {success_rate['total_transactions']:,} successful transactions
✅ {success_rate['success_rate_percent']:.1f}% success rate
✅ {trust_savings['fraud_prevented_algo']:.1f} ALGO fraud prevented

BUSINESS MODEL:
0.5% platform fee + merchant services + premium features = $500K/year at 50K students

COMPETITIVE ADVANTAGE:
Network effects + campus partnerships + multi-use platform = winner-take-all

ASK:
$500K to expand from 1 campus to 10 campuses in 6 months
"""
        
        investor_one_pager = f"""
ALGOCHAT PAY - INVESTOR ONE-PAGER
Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M')}

MARKET OPPORTUNITY:
- 4,000+ US universities, 20M students
- $200B+ annual student spending
- Fintech + Blockchain intersection
- Target: 1% penetration = $2B opportunity

PRODUCT:
WhatsApp blockchain wallet for students
Multi-use: Payments + NFT tickets + fundraising
Built on Algorand for speed + low cost

TRACTION (Current):
- {adoption['total_users']} active students
- {adoption['activation_rate_percent']:.0f}% activation rate
- {success_rate['total_transactions']:,} transactions processed
- {success_rate['success_rate_percent']:.1f}% success rate

UNIT ECONOMICS:
- CAC: $5-10 (viral + student ambassadors)
- Revenue: 0.5% per transaction
- LTV: $50+ (2 txs/day × 0.5% × $20 avg × 365 days × 2 years)
- LTV/CAC: 5-10x

GO-TO-MARKET:
Campus-by-campus expansion
Student ambassadors + viral growth
University partnerships for official endorsement

FUNDING:
Raising: $500K seed
Use: 10 campus expansion, 5K students, merchant SDK
Timeline: 6 months to milestones

TEAM:
[Your team details here]

ROUND SIZE: $500K
CURRENT VALUATION: [TBD]
CONTACT: [Your email]
"""
        
        press_release = f"""
PRESS RELEASE - FOR IMMEDIATE RELEASE
{self.timestamp.strftime('%B %d, %Y')}

Student Startup AlgoChat Pay Reaches {adoption['total_users']} Users, 
Processes {success_rate['total_transactions']:,} Blockchain Transactions

WhatsApp-Based Wallet Simplifies Campus Payments with {success_rate['success_rate_percent']:.1f}% Success Rate

[CITY, STATE] - AlgoChat Pay, a blockchain-based payment platform for college students, 
announced today that it has reached {adoption['total_users']} active users with a 
{adoption['activation_rate_percent']:.0f}% activation rate, proving strong product-market fit 
in the student payment market.

Built on Algorand blockchain, AlgoChat Pay enables students to send payments, purchase 
NFT event tickets, and contribute to fundraising campaigns - all through WhatsApp. 
The platform has processed {success_rate['total_transactions']:,} transactions with a 
{success_rate['success_rate_percent']:.1f}% success rate.

"Students don't want another app to download," said [Founder Name]. "By integrating with 
WhatsApp, we've eliminated the biggest barrier to adoption. Our {adoption['activation_rate_percent']:.0f}% 
activation rate proves students actually USE this, not just sign up and forget."

The platform has prevented {trust_savings['fraud_prevented_algo']:.1f} ALGO in fraud through 
blockchain immutability and saved ${trust_savings['dispute_resolution_savings_usd']:.0f} in 
dispute resolution costs compared to traditional payment methods.

AlgoChat Pay is currently raising a $500K seed round to expand from its initial campus 
to 10 universities over the next 6 months.

For more information, visit [website] or contact [email].

###
"""
        
        return {
            "judge_one_pager": judge_one_pager,
            "investor_one_pager": investor_one_pager,
            "press_release": press_release
        }
    
    def export_all_formats(self, output_dir: str = "pitch_exports"):
        """
        Export all formats to files
        """
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp_str = self.timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Export slide bullets
        slide_bullets = self.export_slide_bullets()
        slides_file = output_path / f"pitch_slides_{timestamp_str}.md"
        with open(slides_file, 'w') as f:
            f.write("# ALGOCHAT PAY PITCH DECK - SLIDE BULLETS\n\n")
            f.write(f"Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M')}\n\n")
            for slide_name, bullets in slide_bullets.items():
                f.write(f"## {slide_name.replace('_', ' ')}\n\n")
                for bullet in bullets:
                    f.write(f"- {bullet}\n")
                f.write("\n")
        
        # Export speaker notes
        speaker_notes = self.export_speaker_notes()
        notes_file = output_path / f"speaker_notes_{timestamp_str}.md"
        with open(notes_file, 'w') as f:
            f.write("# ALGOCHAT PAY PITCH - SPEAKER NOTES\n\n")
            f.write(f"Generated: {self.timestamp.strftime('%Y-%m-%d %H:%M')}\n\n")
            for section, notes in speaker_notes.items():
                f.write(f"## {section}\n\n")
                f.write(notes.strip() + "\n\n")
        
        # Export one-pagers
        one_pagers = self.export_one_pagers()
        for name, content in one_pagers.items():
            file_path = output_path / f"{name}_{timestamp_str}.txt"
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Export JSON for programmatic access
        comprehensive_metrics = {
            "adoption": self.pitch_service.get_adoption_rate(),
            "daily_active": self.pitch_service.get_daily_active_wallets(),
            "transactions_per_user": self.pitch_service.get_avg_transactions_per_user(),
            "campus_coverage": self.pitch_service.get_campus_coverage(),
            "trust_savings": self.pitch_service.get_trust_savings(),
            "impact_statements": self.pitch_service.get_judge_impact_statements(),
            "elevator_pitch": self.pitch_service.get_elevator_pitch_stats(),
            "success_rate": self.demo_service.get_success_rate_metrics(),
            "settlement_time": self.demo_service.get_average_settlement_time(),
            "tickets": self.demo_service.get_ticket_metrics(),
            "fundraising": self.demo_service.get_fundraising_metrics(),
            "timestamp": self.timestamp.isoformat()
        }
        
        json_file = output_path / f"pitch_metrics_{timestamp_str}.json"
        with open(json_file, 'w') as f:
            json.dump(comprehensive_metrics, f, indent=2)
        
        return {
            "slides": str(slides_file),
            "speaker_notes": str(notes_file),
            "judge_one_pager": str(output_path / f"judge_one_pager_{timestamp_str}.txt"),
            "investor_one_pager": str(output_path / f"investor_one_pager_{timestamp_str}.txt"),
            "press_release": str(output_path / f"press_release_{timestamp_str}.txt"),
            "json_metrics": str(json_file)
        }


def main():
    """CLI execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Final Pitch Stats Export"
    )
    
    parser.add_argument(
        "--output-dir",
        default="pitch_exports",
        help="Output directory for exports"
    )
    
    parser.add_argument(
        "--format",
        choices=["all", "slides", "notes", "onepager", "json"],
        default="all",
        help="Export format"
    )
    
    args = parser.parse_args()
    
    # Create database session
    db = SessionLocal()
    
    try:
        exporter = FinalPitchExporter(db)
        
        print("\n" + "="*80)
        print("FINAL PITCH STATS EXPORT")
        print("="*80 + "\n")
        
        if args.format == "all":
            files = exporter.export_all_formats(args.output_dir)
            print("✅ Exported all formats:\n")
            for format_name, file_path in files.items():
                print(f"   📄 {format_name}: {file_path}")
        
        elif args.format == "slides":
            bullets = exporter.export_slide_bullets()
            for slide_name, bullets_list in bullets.items():
                print(f"\n{slide_name.replace('_', ' ')}:")
                for bullet in bullets_list:
                    print(f"  - {bullet}")
        
        elif args.format == "notes":
            notes = exporter.export_speaker_notes()
            for section, text in notes.items():
                print(f"\n{section}:")
                print(text)
        
        elif args.format == "onepager":
            one_pagers = exporter.export_one_pagers()
            print(one_pagers['judge_one_pager'])
        
        elif args.format == "json":
            files = exporter.export_all_formats(args.output_dir)
            print(f"✅ JSON metrics: {files['json_metrics']}")
        
        print("\n" + "="*80 + "\n")
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
