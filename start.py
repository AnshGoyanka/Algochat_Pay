#!/usr/bin/env python3
"""
AlgoChat Pay - Quick Start Script
Initializes database and starts the server
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_environment():
    """Check if .env file exists"""
    env_file = project_root / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found!")
        print("   Please copy .env.example to .env and configure it")
        print("   cp .env.example .env")
        return False
    
    print("✅ Environment file found")
    return True


def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import fastapi
        import sqlalchemy
        import algosdk
        import twilio
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("   Run: pip install -r requirements.txt")
        return False


def initialize_database():
    """Initialize database tables"""
    print("\n🗄️  Initializing database...")
    
    try:
        from backend.database import init_db
        init_db()
        print("✅ Database initialized")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def generate_encryption_key():
    """Generate encryption key if not set"""
    from backend.config import settings
    
    if settings.ENCRYPTION_KEY == "your-32-byte-encryption-key-here-change-this":
        print("\n⚠️  WARNING: Using default encryption key!")
        print("   Generate a secure key with:")
        print("   python -c \"from backend.security.encryption import EncryptionService; print(EncryptionService.generate_encryption_key())\"")
        return False
    
    return True


def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting AlgoChat Pay server...")
    print("=" * 60)
    
    import uvicorn
    from backend.config import settings
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )


def main():
    """Main startup routine"""
    print("=" * 60)
    print("🏦 AlgoChat Pay - Campus Wallet on WhatsApp")
    print("=" * 60)
    print()
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    
    # Check encryption key
    generate_encryption_key()
    
    # Start server
    print("\n✨ Initialization complete!")
    print("\n📱 Server will be available at: http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("💬 WhatsApp webhook: http://localhost:8000/webhook/whatsapp")
    print("\n⚡ Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down AlgoChat Pay...")
        print("   Thanks for using AlgoChat Pay!")


if __name__ == "__main__":
    main()
