"""
Integration tests for AlgoChat Pay
Tests complete workflows end-to-end
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

from backend.main import app
from backend.database import Base, get_db
from backend.config import settings

# Test database
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_algochat.db"
engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_basic_health(self):
        """Test basic health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_database_health(self, test_db):
        """Test database health check"""
        response = client.get("/health/db")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "latency_ms" in data
        assert "active_connections" in data
    
    def test_algorand_health(self):
        """Test Algorand network health"""
        with patch("backend.algorand.client.algorand_client.algod_client.status") as mock_status:
            mock_status.return_value = {
                "last-round": 12345,
                "time-since-last-round": 4500000000,
                "catchup-time": 0
            }
            
            response = client.get("/health/algorand")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert "last_round" in data


class TestMetricsEndpoints:
    """Test metrics endpoints"""
    
    def test_metrics_overview(self, test_db):
        """Test system metrics endpoint"""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        
        assert "users" in data
        assert "transactions" in data
        assert "volume" in data
        assert "fundraising" in data
        assert "tickets" in data


class TestWalletCreation:
    """Test wallet creation workflow"""
    
    @patch("backend.algorand.client.algorand_client.create_wallet")
    def test_create_wallet_success(self, mock_create_wallet, test_db):
        """Test successful wallet creation"""
        mock_create_wallet.return_value = (
            "mock_private_key",
            "MOCKADDRESS123456789012345678901234567890123456789012",
            "mock mnemonic phrase"
        )
        
        from backend.services.wallet_service import wallet_service
        from backend.database import SessionLocal
        
        db = SessionLocal()
        try:
            user, created = wallet_service.get_or_create_wallet(db, "+1234567890")
            
            assert created is True
            assert user.phone_number == "+1234567890"
            assert user.wallet_address.startswith("MOCK")
            assert user.encrypted_private_key is not None
        finally:
            db.close()
    
    @patch("backend.algorand.client.algorand_client.create_wallet")
    def test_get_existing_wallet(self, mock_create_wallet, test_db):
        """Test retrieving existing wallet"""
        mock_create_wallet.return_value = (
            "mock_private_key",
            "MOCKADDRESS123456789012345678901234567890123456789012",
            "mock mnemonic phrase"
        )
        
        from backend.services.wallet_service import wallet_service
        from backend.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Create first time
            user1, created1 = wallet_service.get_or_create_wallet(db, "+1234567890")
            assert created1 is True
            
            # Get existing
            user2, created2 = wallet_service.get_or_create_wallet(db, "+1234567890")
            assert created2 is False
            assert user1.id == user2.id
        finally:
            db.close()


class TestPaymentFlow:
    """Test payment workflow"""
    
    @patch("backend.algorand.client.algorand_client.create_wallet")
    @patch("backend.algorand.client.algorand_client.get_balance")
    @patch("backend.algorand.client.algorand_client.send_payment")
    def test_send_payment_success(
        self,
        mock_send_payment,
        mock_get_balance,
        mock_create_wallet,
        test_db
    ):
        """Test successful payment"""
        # Mock responses
        mock_create_wallet.return_value = (
            "mock_private_key",
            "MOCKADDRESS123456789012345678901234567890123456789012",
            "mock mnemonic"
        )
        mock_get_balance.return_value = 100.0  # Sufficient balance
        mock_send_payment.return_value = "MOCKTXID123456789"
        
        from backend.services.wallet_service import wallet_service
        from backend.services.payment_service import payment_service
        from backend.database import SessionLocal
        
        db = SessionLocal()
        try:
            # Create wallets
            sender, _ = wallet_service.get_or_create_wallet(db, "+1111111111")
            receiver, _ = wallet_service.get_or_create_wallet(db, "+2222222222")
            
            # Send payment
            transaction = payment_service.send_payment(
                db=db,
                sender_phone="+1111111111",
                receiver_phone="+2222222222",
                amount=5.0,
                note="Test payment"
            )
            
            assert transaction.tx_id == "MOCKTXID123456789"
            assert transaction.amount == 5.0
            assert transaction.status.value == "confirmed"
        finally:
            db.close()
    
    @patch("backend.algorand.client.algorand_client.create_wallet")
    @patch("backend.algorand.client.algorand_client.get_balance")
    def test_send_payment_insufficient_balance(
        self,
        mock_get_balance,
        mock_create_wallet,
        test_db
    ):
        """Test payment with insufficient balance"""
        mock_create_wallet.return_value = (
            "mock_private_key",
            "MOCKADDRESS123456789012345678901234567890123456789012",
            "mock mnemonic"
        )
        mock_get_balance.return_value = 1.0  # Insufficient
        
        from backend.services.wallet_service import wallet_service
        from backend.services.payment_service import payment_service
        from backend.database import SessionLocal
        
        db = SessionLocal()
        try:
            wallet_service.get_or_create_wallet(db, "+1111111111")
            wallet_service.get_or_create_wallet(db, "+2222222222")
            
            with pytest.raises(ValueError, match="Insufficient balance"):
                payment_service.send_payment(
                    db=db,
                    sender_phone="+1111111111",
                    receiver_phone="+2222222222",
                    amount=10.0
                )
        finally:
            db.close()


class TestSecurityFeatures:
    """Test security features"""
    
    def test_rate_limiting(self):
        """Test rate limiting middleware"""
        from backend.security.security_utils import phone_rate_limiter
        
        # Reset limiter
        phone_rate_limiter.reset("+1234567890")
        
        # Make requests up to limit
        for i in range(settings.RATE_LIMIT_PER_MINUTE):
            assert phone_rate_limiter.is_allowed("+1234567890") is True
        
        # Next request should be rate limited
        assert phone_rate_limiter.is_allowed("+1234567890") is False
    
    def test_command_injection_detection(self):
        """Test command injection detection"""
        from backend.security.security_utils import CommandInjectionValidator
        
        # Safe inputs
        assert CommandInjectionValidator.is_safe("send +1234567890 5") is True
        assert CommandInjectionValidator.is_safe("balance") is True
        
        # Malicious inputs
        assert CommandInjectionValidator.is_safe("balance; rm -rf /") is False
        assert CommandInjectionValidator.is_safe("send ../../../etc/passwd") is False
        assert CommandInjectionValidator.is_safe("__import__('os').system('ls')") is False
    
    def test_transaction_limits(self):
        """Test transaction limits"""
        from backend.security.security_utils import transaction_limits
        
        # Reset limits for test user
        transaction_limits.daily_totals.clear()
        transaction_limits.daily_counts.clear()
        
        # Within single transaction limit
        allowed, error = transaction_limits.check_limits("+1234567890", 50.0)
        assert allowed is True
        
        # Exceed single transaction limit
        allowed, error = transaction_limits.check_limits("+1234567890", 150.0)
        assert allowed is False
        assert "Transaction amount exceeds limit" in error


class TestDemoSafetyRetry:
    """Test retry logic and fallback"""
    
    @patch("backend.algorand.client.algorand_client._get_active_client")
    def test_automatic_retry_on_failure(self, mock_get_client, test_db):
        """Test automatic retry with exponential backoff"""
        from backend.utils.demo_safety import with_retry, RetryConfig
        
        call_count = 0
        
        @with_retry(RetryConfig(max_attempts=3, initial_delay=0.01))
        def flaky_operation():
            nonlocal call_count
            call_count += 1
            
            if call_count < 3:
                raise Exception("Temporary failure")
            
            return "success"
        
        result = flaky_operation()
        
        assert result == "success"
        assert call_count == 3  # Failed twice, succeeded on third attempt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
