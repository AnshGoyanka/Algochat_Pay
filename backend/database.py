"""
Database connection and session management
Uses SQLAlchemy with PostgreSQL (with SQLite fallback)
"""
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging
import os
from backend.config import settings

logger = logging.getLogger(__name__)

# Try to create PostgreSQL engine, fallback to SQLite if it fails
def create_db_engine():
    """Create database engine with automatic fallback to SQLite"""
    try:
        # Try PostgreSQL first
        engine = create_engine(
            settings.DATABASE_URL,
            echo=settings.DB_ECHO,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            connect_args={"connect_timeout": 5}  # 5 second timeout
        )
        # Test the connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ Connected to PostgreSQL database")
        return engine
    except Exception as e:
        if settings.USE_SQLITE_FALLBACK:
            logger.warning(f"PostgreSQL connection failed: {e}")
            logger.info("→ Falling back to SQLite for local development")
            
            # Create data directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            # Use SQLite
            sqlite_url = "sqlite:///data/algochat_local.db"
            engine = create_engine(
                sqlite_url,
                echo=settings.DB_ECHO,
                connect_args={"check_same_thread": False}
            )
            logger.info(f"✓ Connected to SQLite database: {sqlite_url}")
            return engine
        else:
            logger.error(f"Database connection failed: {e}")
            raise

# Create database engine
engine = create_db_engine()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes
    Provides database session with automatic cleanup
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables
    Call this on application startup
    """
    from backend.models import user, transaction, fund, ticket, event, split, merchant
    Base.metadata.create_all(bind=engine)
