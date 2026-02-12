"""
Pytest configuration
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment"""
    import os
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"
    os.environ["ENCRYPTION_KEY"] = "test_encryption_key_32_bytes_!!"
    os.environ["TWILIO_ACCOUNT_SID"] = "test_sid"
    os.environ["TWILIO_AUTH_TOKEN"] = "test_token"
    os.environ["TWILIO_WHATSAPP_NUMBER"] = "+1234567890"
    os.environ["TWILIO_WEBHOOK_URL"] = "http://localhost:8000/webhook"
    os.environ["REDIS_ENABLED"] = "false"
