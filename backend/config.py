"""
Configuration management for AlgoChat Pay
Loads environment variables and provides typed config access
"""
import os
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration"""
    
    # Application
    APP_NAME: str = "AlgoChat Pay"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    
    # Database
    DATABASE_URL: str
    DB_ECHO: bool = False
    USE_SQLITE_FALLBACK: bool = True  # Use SQLite if PostgreSQL fails
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False
    
    # Algorand
    ALGORAND_NETWORK: str = "testnet"
    ALGORAND_ALGOD_ADDRESS: str = "https://testnet-api.algonode.cloud"
    ALGORAND_ALGOD_TOKEN: str = ""
    ALGORAND_INDEXER_ADDRESS: str = "https://testnet-idx.algonode.cloud"
    ALGORAND_INDEXER_TOKEN: str = ""
    
    # Encryption (32-byte key for AES-256)
    ENCRYPTION_KEY: str
    
    # Twilio
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_WHATSAPP_NUMBER: str
    TWILIO_WEBHOOK_URL: str
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/algochat.log"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_testnet(self) -> bool:
        return self.ALGORAND_NETWORK == "testnet"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
