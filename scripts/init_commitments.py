"""
Create commitment tables in database
Run this to initialize the payment commitment feature
"""
from backend.database import engine, Base
from backend.models.commitment import (
    PaymentCommitment,
    CommitmentParticipant,
    CommitmentReminder,
    ReliabilityScore
)
from sqlalchemy import text

def create_commitment_tables():
    """Create all commitment-related tables"""
    print("Creating commitment tables...")
    
    # Drop existing tables first (if they exist)
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS commitment_reminders CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS commitment_participants CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS payment_commitments CASCADE"))
        conn.execute(text("DROP TABLE IF EXISTS reliability_scores CASCADE"))
        conn.commit()
    
    print("✓ Dropped existing tables")
    
    # Create tables
    Base.metadata.create_all(bind=engine, tables=[
        PaymentCommitment.__table__,
        CommitmentParticipant.__table__,
        CommitmentReminder.__table__,
        ReliabilityScore.__table__
    ])
    
    print("✅ Commitment tables created successfully!")
    print("\nNew tables:")
    print("  - payment_commitments")
    print("  - commitment_participants")
    print("  - commitment_reminders")
    print("  - reliability_scores")
    print("\n🚀 Payment Lock Commitments feature is ready!")


if __name__ == "__main__":
    create_commitment_tables()
