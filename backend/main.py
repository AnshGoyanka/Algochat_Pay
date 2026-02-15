"""
AlgoChat Pay - Main FastAPI Application
Campus Wallet on WhatsApp & Telegram powered by Algorand
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from backend.config import settings
from backend.database import init_db
from backend.utils.production_logging import ProductionLogger
from backend.middleware import LoggingMiddleware, SecurityLoggingMiddleware
from backend.security.security_utils import RateLimitMiddleware
from bot import whatsapp_router, telegram_router
from backend.routes import health_router, metrics_router, admin_router, demo_router, freeze_router

# Setup production logging
ProductionLogger.setup(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE,
    enable_json=True
)

logger = ProductionLogger.get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Campus Wallet on WhatsApp & Telegram - Powered by Algorand",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware (add first for complete request tracking)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(whatsapp_router, tags=["WhatsApp"])
app.include_router(telegram_router, tags=["Telegram"])
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(admin_router)
app.include_router(demo_router)
app.include_router(freeze_router)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Algorand Network: {settings.ALGORAND_NETWORK}")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down AlgoChat Pay")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "algorand_network": settings.ALGORAND_NETWORK,
        "docs": "/docs" if settings.DEBUG else "disabled",
        "database": "connected",
        "algorand": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
