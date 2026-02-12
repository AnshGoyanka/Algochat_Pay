"""
Campus Usage Simulator
Generates realistic transaction history for 500 students across 30 days
Creates: Payments, Bill Splits, Tickets, Fundraising campaigns
"""
import sys
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import SessionLocal
from backend.models.user import User
from backend.models.transaction import Transaction, TransactionStatus, TransactionType
from backend.models.fund import Fund
from backend.models.ticket import Ticket
from backend.security.encryption import encryption_service
from backend.utils.production_logging import ProductionLogger

logger = ProductionLogger.get_logger(__name__)


class CampusSimulator:
    """
    Simulates realistic campus wallet usage patterns
    """
    
    # Campus demographics
    TOTAL_STUDENTS = 500
    ACTIVE_PERCENTAGE = 0.75  # 75% active users
    
    # Transaction patterns
    AVG_TRANSACTIONS_PER_USER = 8  # Over 30 days
    PAYMENT_AMOUNT_RANGE = (2.0, 50.0)
    BILL_SPLIT_RANGE = (20.0, 100.0)
    TICKET_PRICE_RANGE = (5.0, 25.0)
    DONATION_RANGE = (5.0, 100.0)
    
    # Campus clubs
    CLUBS = [
        {"name": "Tech Club", "president": None},
        {"name": "Drama Society", "president": None},
        {"name": "Sports Committee", "president": None}
    ]
    
    # Campus events
    EVENTS = [
        {"name": "TechFest 2026", "date": "2026-02-20", "tickets_sold": 312},
        {"name": "Spring Concert", "date": "2026-02-15", "tickets_sold": 289}
    ]
    
    # Fundraising campaigns
    FUNDRAISERS = [
        {"title": "Hostel Mess Pool", "goal": 2500.0, "description": "Monthly mess expenses"},
        {"title": "Help Campus Food Bank", "goal": 1000.0, "description": "Support students in need"},
        {"title": "Library Book Drive", "goal": 500.0, "description": "Buy new textbooks"},
        {"title": "Sports Equipment Fund", "goal": 3000.0, "description": "New sports gear"},
        {"title": "Tech Lab Upgrade", "goal": 5000.0, "description": "New computers and equipment"}
    ]
    
    # Common campus transaction notes
    PAYMENT_NOTES = [
        "lunch", "coffee", "textbook", "lab fees", "canteen",
        "printing", "hostel dues", "project expenses", "dinner split",
        "cab share", "movie ticket", "game purchase", "stationery"
    ]
    
    def __init__(self, days_back: int = 30):
        self.db = SessionLocal()
        self.days_back = days_back
        self.start_date = datetime.utcnow() - timedelta(days=days_back)
        self.students: List[User] = []
        self.club_presidents: List[User] = []
        
    def generate_phone_number(self, index: int) -> str:
        """Generate realistic campus phone numbers"""
        # US campus numbers: +1 (415) 555-XXXX
        return f"+1415555{2000 + index:04d}"
    
    def generate_wallet_address(self) -> str:
        """Generate mock Algorand address"""
        import hashlib
        seed = str(random.random()).encode()
        hash_val = hashlib.sha256(seed).hexdigest()[:52].upper()
        # Algorand addresses are 58 chars, base32
        return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ234567', k=58))
    
    def create_students(self):
        """Create 500 student wallets"""
        print(f"\n📱 Creating {self.TOTAL_STUDENTS} student wallets...")
        
        for i in range(self.TOTAL_STUDENTS):
            phone = self.generate_phone_number(i)
            
            # Check if exists
            existing = self.db.query(User).filter(User.phone_number == phone).first()
            if existing:
                self.students.append(existing)
                continue
            
            # Create new user
            wallet_address = self.generate_wallet_address()
            
            # Mock encrypted private key
            encrypted_key = encryption_service.encrypt_private_key(
                f"mock_private_key_{i}_{random.randint(10000, 99999)}"
            )
            
            # Vary creation dates
            created_at = self.start_date + timedelta(
                days=random.uniform(0, self.days_back * 0.8)
            )
            
            user = User(
                phone_number=phone,
                wallet_address=wallet_address,
                encrypted_private_key=encrypted_key,
                is_active=random.random() < self.ACTIVE_PERCENTAGE,
                created_at=created_at
            )
            
            self.db.add(user)
            self.students.append(user)
            
            if (i + 1) % 50 == 0:
                print(f"  ✅ Created {i + 1} students...")
        
        self.db.commit()
        print(f"  🎉 Total students: {len(self.students)}")
        
        # Select club presidents
        self.club_presidents = random.sample(self.students, len(self.CLUBS))
        for i, club in enumerate(self.CLUBS):
            club["president"] = self.club_presidents[i]
    
    def generate_peer_payments(self):
        """Generate realistic peer-to-peer payments"""
        print("\n💸 Generating peer-to-peer payments...")
        
        active_students = [s for s in self.students if s.is_active]
        num_payments = int(len(active_students) * self.AVG_TRANSACTIONS_PER_USER * 0.5)
        
        for i in range(num_payments):
            sender = random.choice(active_students)
            receiver = random.choice([s for s in active_students if s.id != sender.id])
            
            amount = round(random.uniform(*self.PAYMENT_AMOUNT_RANGE), 2)
            note = random.choice(self.PAYMENT_NOTES)
            
            # Random timestamp within 30 days
            timestamp = self.start_date + timedelta(
                days=random.uniform(0, self.days_back),
                hours=random.randint(8, 22),  # Campus hours
                minutes=random.randint(0, 59)
            )
            
            # 98% success rate
            status = TransactionStatus.CONFIRMED if random.random() < 0.98 else TransactionStatus.FAILED
            
            tx_id = f"SIM{random.randint(100000, 999999)}{i}" if status == TransactionStatus.CONFIRMED else None
            confirmed_at = timestamp + timedelta(seconds=random.uniform(4, 6)) if status == TransactionStatus.CONFIRMED else None
            
            transaction = Transaction(
                sender_phone=sender.phone_number,
                sender_address=sender.wallet_address,
                receiver_phone=receiver.phone_number,
                receiver_address=receiver.wallet_address,
                amount=amount,
                transaction_type=TransactionType.SEND,
                status=status,
                tx_id=tx_id,
                note=note,
                timestamp=timestamp,
                confirmed_at=confirmed_at
            )
            
            self.db.add(transaction)
            
            if (i + 1) % 100 == 0:
                print(f"  💰 Generated {i + 1} payments...")
                self.db.commit()
        
        self.db.commit()
        print(f"  ✅ Total payments: {num_payments}")
    
    def generate_bill_splits(self):
        """Generate group bill splitting transactions"""
        print("\n🍽️ Generating bill splits...")
        
        active_students = [s for s in self.students if s.is_active]
        num_splits = int(len(active_students) * 0.1)  # 10% have split bills
        
        split_notes = [
            "dinner at restaurant",
            "pizza order",
            "group project supplies",
            "weekend trip",
            "birthday celebration",
            "hostel party",
            "hackathon food",
            "study group snacks"
        ]
        
        for i in range(num_splits):
            # 3-5 people per split
            group_size = random.randint(3, 5)
            group = random.sample(active_students, group_size)
            
            total_amount = round(random.uniform(*self.BILL_SPLIT_RANGE), 2)
            per_person = round(total_amount / group_size, 2)
            note = random.choice(split_notes)
            
            timestamp = self.start_date + timedelta(
                days=random.uniform(0, self.days_back),
                hours=random.randint(12, 21),
                minutes=random.randint(0, 59)
            )
            
            # First person initiates
            initiator = group[0]
            
            # Others pay their share
            for payer in group[1:]:
                status = TransactionStatus.CONFIRMED if random.random() < 0.95 else TransactionStatus.PENDING
                
                tx_id = f"SPLIT{random.randint(100000, 999999)}{i}" if status == TransactionStatus.CONFIRMED else None
                confirmed_at = timestamp + timedelta(seconds=random.uniform(4, 6)) if status == TransactionStatus.CONFIRMED else None
                
                transaction = Transaction(
                    sender_phone=payer.phone_number,
                    sender_address=payer.wallet_address,
                    receiver_phone=initiator.phone_number,
                    receiver_address=initiator.wallet_address,
                    amount=per_person,
                    transaction_type=TransactionType.SPLIT,
                    status=status,
                    tx_id=tx_id,
                    note=f"Split: {note}",
                    timestamp=timestamp,
                    confirmed_at=confirmed_at
                )
                
                self.db.add(transaction)
        
        self.db.commit()
        print(f"  ✅ Total bill splits: {num_splits}")
    
    def generate_fundraising_campaigns(self):
        """Generate campus fundraising campaigns"""
        print("\n❤️ Generating fundraising campaigns...")
        
        for i, fundraiser in enumerate(self.FUNDRAISERS):
            president = self.club_presidents[i % len(self.club_presidents)]
            
            created_at = self.start_date + timedelta(days=random.randint(0, 10))
            deadline = created_at + timedelta(days=random.randint(30, 90))
            
            # Random progress (30% to 120% of goal)
            progress_percentage = random.uniform(0.3, 1.2)
            current_amount = round(fundraiser["goal"] * progress_percentage, 2)
            is_goal_met = current_amount >= fundraiser["goal"]
            
            # Number of contributors
            contributors_count = random.randint(15, 80)
            
            fund = Fund(
                title=fundraiser["title"],
                description=fundraiser["description"],
                goal_amount=fundraiser["goal"],
                current_amount=current_amount,
                creator_phone=president.phone_number,
                creator_address=president.wallet_address,
                deadline=deadline,
                is_goal_met=is_goal_met,
                is_active=not is_goal_met,
                contributors_count=contributors_count,
                created_at=created_at
            )
            
            self.db.add(fund)
            self.db.flush()  # Get fund.id
            
            # Generate contributions
            active_students = [s for s in self.students if s.is_active]
            contributors = random.sample(active_students, min(contributors_count, len(active_students)))
            
            for contributor in contributors:
                amount = round(random.uniform(*self.DONATION_RANGE), 2)
                
                contribution_time = created_at + timedelta(
                    days=random.uniform(0, (deadline - created_at).days),
                    hours=random.randint(8, 22)
                )
                
                tx_id = f"FUND{fund.id}{random.randint(1000, 9999)}"
                
                transaction = Transaction(
                    sender_phone=contributor.phone_number,
                    sender_address=contributor.wallet_address,
                    receiver_phone=president.phone_number,
                    receiver_address=president.wallet_address,
                    amount=amount,
                    transaction_type=TransactionType.FUND,
                    status=TransactionStatus.CONFIRMED,
                    tx_id=tx_id,
                    note=f"Donation to: {fund.title}",
                    timestamp=contribution_time,
                    confirmed_at=contribution_time + timedelta(seconds=random.uniform(4, 6))
                )
                
                self.db.add(transaction)
        
        self.db.commit()
        print(f"  ✅ Total fundraisers: {len(self.FUNDRAISERS)}")
    
    def generate_event_tickets(self):
        """Generate NFT ticket purchases for campus events"""
        print("\n🎫 Generating event ticket sales...")
        
        active_students = [s for s in self.students if s.is_active]
        
        for event in self.EVENTS:
            event_date = datetime.strptime(event["date"], "%Y-%m-%d")
            tickets_to_sell = event["tickets_sold"]
            
            # Ticket sales start 2 weeks before event
            sale_start = event_date - timedelta(days=14)
            
            # Select buyers
            buyers = random.sample(active_students, min(tickets_to_sell, len(active_students)))
            
            for i, buyer in enumerate(buyers):
                ticket_price = round(random.uniform(*self.TICKET_PRICE_RANGE), 2)
                
                # Most tickets sold in last week
                days_before = random.uniform(0, 14) ** 2 / 14  # Weighted toward event date
                purchase_time = sale_start + timedelta(days=days_before)
                
                # Generate unique ticket number
                ticket_number = f"{event['name'][:4].upper()}{2026}{i+1:04d}"
                
                # Mock NFT asset ID
                asset_id = 100000 + len(self.EVENTS) * 1000 + i
                
                ticket = Ticket(
                    owner_phone=buyer.phone_number,
                    owner_address=buyer.wallet_address,
                    event_name=event["name"],
                    ticket_number=ticket_number,
                    asset_id=asset_id,
                    price=ticket_price,
                    is_valid=True,
                    is_used=event_date < datetime.utcnow(),  # Used if event passed
                    created_at=purchase_time
                )
                
                self.db.add(ticket)
                
                # Create payment transaction
                # Assume event organizer is first club president
                organizer = self.club_presidents[0]
                
                tx_id = f"TKT{asset_id}"
                
                transaction = Transaction(
                    sender_phone=buyer.phone_number,
                    sender_address=buyer.wallet_address,
                    receiver_phone=organizer.phone_number,
                    receiver_address=organizer.wallet_address,
                    amount=ticket_price,
                    transaction_type=TransactionType.TICKET,
                    status=TransactionStatus.CONFIRMED,
                    tx_id=tx_id,
                    note=f"Ticket: {event['name']}",
                    timestamp=purchase_time,
                    confirmed_at=purchase_time + timedelta(seconds=random.uniform(4, 6))
                )
                
                self.db.add(transaction)
            
            print(f"  🎟️  {event['name']}: {len(buyers)} tickets")
        
        self.db.commit()
        print(f"  ✅ Total tickets minted: {sum(e['tickets_sold'] for e in self.EVENTS)}")
    
    def generate_statistics_summary(self):
        """Print final summary statistics"""
        print("\n" + "="*60)
        print("📊 CAMPUS SIMULATION SUMMARY")
        print("="*60)
        
        # User stats
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        
        # Transaction stats
        total_txs = self.db.query(Transaction).count()
        confirmed_txs = self.db.query(Transaction).filter(
            Transaction.status == TransactionStatus.CONFIRMED
        ).count()
        
        from sqlalchemy import func
        total_volume = self.db.query(func.sum(Transaction.amount)).filter(
            Transaction.status == TransactionStatus.CONFIRMED
        ).scalar() or 0.0
        
        # Fundraising stats
        total_funds = self.db.query(Fund).count()
        active_funds = self.db.query(Fund).filter(Fund.is_active == True).count()
        total_raised = self.db.query(func.sum(Fund.current_amount)).scalar() or 0.0
        
        # Ticket stats
        total_tickets = self.db.query(Ticket).count()
        
        print(f"\n👥 USERS:")
        print(f"   Total Wallets: {total_users}")
        print(f"   Active Users: {active_users} ({active_users/total_users*100:.1f}%)")
        
        print(f"\n💰 TRANSACTIONS:")
        print(f"   Total Transactions: {total_txs}")
        print(f"   Confirmed: {confirmed_txs}")
        print(f"   Success Rate: {confirmed_txs/total_txs*100:.1f}%")
        print(f"   Total Volume: {total_volume:.2f} ALGO")
        print(f"   Average Transaction: {total_volume/confirmed_txs:.2f} ALGO")
        
        print(f"\n❤️ FUNDRAISING:")
        print(f"   Total Campaigns: {total_funds}")
        print(f"   Active Campaigns: {active_funds}")
        print(f"   Total Raised: {total_raised:.2f} ALGO")
        
        print(f"\n🎫 TICKETS:")
        print(f"   Total Minted: {total_tickets}")
        
        print("\n" + "="*60)
        print("✅ SIMULATION COMPLETE")
        print("="*60 + "\n")
    
    def run_full_simulation(self):
        """Execute complete campus simulation"""
        print("\n" + "🎬"*30)
        print("CAMPUS USAGE SIMULATOR - 30 DAYS")
        print("🎬"*30)
        
        try:
            self.create_students()
            self.generate_peer_payments()
            self.generate_bill_splits()
            self.generate_fundraising_campaigns()
            self.generate_event_tickets()
            self.generate_statistics_summary()
            
            print("🚀 Simulation data ready for demo!")
            return True
            
        except Exception as e:
            print(f"\n❌ Simulation failed: {e}")
            import traceback
            traceback.print_exc()
            self.db.rollback()
            return False
        finally:
            self.db.close()


def main():
    """
    Main entry point
    
    Usage:
        python scripts/campus_simulation.py
    """
    print("\n⚠️  WARNING: This will populate the database with simulated data.")
    print("   Make sure you're using a test database!\n")
    
    response = input("Continue? (yes/no): ").lower()
    if response != "yes":
        print("Aborted.")
        return
    
    simulator = CampusSimulator(days_back=30)
    success = simulator.run_full_simulation()
    
    if success:
        print("\n✅ Demo data is ready!")
        print("\nNext steps:")
        print("1. Start backend: uvicorn backend.main:app --reload")
        print("2. Check metrics: curl http://localhost:8000/metrics")
        print("3. View dashboard: curl http://localhost:8000/admin/dashboard")
    else:
        print("\n❌ Simulation incomplete. Check errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
