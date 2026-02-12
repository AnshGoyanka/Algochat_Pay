"""
Unit tests for wallet service
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pytest
from backend.services.wallet_service import wallet_service
from backend.database import SessionLocal, init_db
from backend.models.user import User


@pytest.fixture
def db_session():
    """Create database session for tests"""
    init_db()
    db = SessionLocal()
    yield db
    db.close()


def test_create_wallet(db_session):
    """Test wallet creation"""
    phone = "+919999999999"
    
    user, created = wallet_service.get_or_create_wallet(db_session, phone)
    
    assert created is True
    assert user.phone_number == phone
    assert len(user.wallet_address) == 58  # Algorand address length
    assert user.encrypted_private_key is not None
    
    print(f"✅ Wallet created: {user.wallet_address}")


def test_get_existing_wallet(db_session):
    """Test retrieving existing wallet"""
    phone = "+919999999998"
    
    # Create wallet
    user1, created1 = wallet_service.get_or_create_wallet(db_session, phone)
    assert created1 is True
    
    # Get same wallet
    user2, created2 = wallet_service.get_or_create_wallet(db_session, phone)
    assert created2 is False
    assert user1.wallet_address == user2.wallet_address
    
    print(f"✅ Retrieved existing wallet: {user2.wallet_address}")


def test_invalid_phone(db_session):
    """Test invalid phone number"""
    with pytest.raises(ValueError):
        wallet_service.get_or_create_wallet(db_session, "invalid_phone")
    
    print("✅ Invalid phone rejected")


def test_get_balance(db_session):
    """Test balance retrieval"""
    phone = "+919999999997"
    
    user, _ = wallet_service.get_or_create_wallet(db_session, phone)
    balance = wallet_service.get_balance(db_session, phone)
    
    assert balance >= 0
    print(f"✅ Balance retrieved: {balance} ALGO")


def test_wallet_info(db_session):
    """Test wallet info retrieval"""
    phone = "+919999999996"
    
    user, _ = wallet_service.get_or_create_wallet(db_session, phone)
    info = wallet_service.get_wallet_info(db_session, phone)
    
    assert info["phone"] == phone
    assert info["address"] == user.wallet_address
    assert "balance" in info
    
    print(f"✅ Wallet info: {info}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
