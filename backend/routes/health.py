"""
Health check and monitoring endpoints
Provides system health status for observability
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import time
from typing import Dict, Any
from datetime import datetime

from backend.database import get_db
from backend.algorand.client import algorand_client
from backend.config import settings
from backend.utils.production_logging import ProductionLogger

router = APIRouter(prefix="/health", tags=["Health"])
logger = ProductionLogger.get_logger(__name__)


@router.get("")
async def health_check():
    """
    Basic health check
    Returns 200 if service is running
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/db")
async def health_check_database(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Database health check
    Tests PostgreSQL connection and query performance
    """
    start_time = time.time()
    
    try:
        # Test database connectivity
        result = db.execute(text("SELECT 1")).scalar()
        
        if result != 1:
            raise Exception("Database query returned unexpected result")
        
        # Get database stats
        db_size_result = db.execute(text(
            "SELECT pg_database_size(current_database())"
        )).scalar()
        
        connection_count = db.execute(text(
            "SELECT count(*) FROM pg_stat_activity"
        )).scalar()
        
        latency_ms = (time.time() - start_time) * 1000
        
        status = {
            "status": "healthy",
            "database": "postgresql",
            "latency_ms": round(latency_ms, 2),
            "database_size_mb": round(db_size_result / 1024 / 1024, 2) if db_size_result else 0,
            "active_connections": connection_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Warn if latency is high
        if latency_ms > 100:
            logger.warning(f"Database latency high: {latency_ms:.2f}ms")
            status["warning"] = "High latency detected"
        
        return status
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "database": "postgresql",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/algorand")
async def health_check_algorand() -> Dict[str, Any]:
    """
    Algorand network health check
    Tests connection to Algorand node and retrieves network status
    """
    start_time = time.time()
    
    try:
        # Get node status
        status_result = algorand_client.algod_client.status()
        
        # Get suggested params (tests transaction readiness)
        params = algorand_client.algod_client.suggested_params()
        
        latency_ms = (time.time() - start_time) * 1000
        
        health_status = {
            "status": "healthy",
            "network": settings.ALGORAND_NETWORK,
            "node_address": settings.ALGORAND_ALGOD_ADDRESS,
            "latency_ms": round(latency_ms, 2),
            "last_round": status_result.get("last-round"),
            "time_since_last_round": status_result.get("time-since-last-round"),
            "catchup_time": status_result.get("catchup-time", 0),
            "min_fee": params.min_fee,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Warn if node is catching up
        if status_result.get("catchup-time", 0) > 0:
            logger.warning("Algorand node is catching up")
            health_status["warning"] = "Node is synchronizing"
        
        # Warn if latency is high
        if latency_ms > 2000:
            logger.warning(f"Algorand node latency high: {latency_ms:.2f}ms")
            health_status["warning"] = "High latency detected"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Algorand health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "network": settings.ALGORAND_NETWORK,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/redis")
async def health_check_redis() -> Dict[str, Any]:
    """
    Redis health check
    Tests connection to Redis cache
    """
    if not settings.REDIS_ENABLED:
        return {
            "status": "disabled",
            "message": "Redis is not enabled",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    start_time = time.time()
    
    try:
        import redis
        
        # Connect to Redis
        r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        
        # Test ping
        r.ping()
        
        # Get info
        info = r.info()
        
        latency_ms = (time.time() - start_time) * 1000
        
        return {
            "status": "healthy",
            "redis": "connected",
            "latency_ms": round(latency_ms, 2),
            "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
            "connected_clients": info.get("connected_clients", 0),
            "uptime_days": round(info.get("uptime_in_seconds", 0) / 86400, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Redis health check failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail={
                "status": "unhealthy",
                "redis": "disconnected",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )


@router.get("/all")
async def health_check_all(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Comprehensive health check
    Tests all system components
    """
    results = {
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    all_healthy = True
    
    # Check database
    try:
        db_health = await health_check_database(db)
        results["checks"]["database"] = db_health
    except HTTPException as e:
        results["checks"]["database"] = e.detail
        all_healthy = False
    
    # Check Algorand
    try:
        algo_health = await health_check_algorand()
        results["checks"]["algorand"] = algo_health
    except HTTPException as e:
        results["checks"]["algorand"] = e.detail
        all_healthy = False
    
    # Check Redis
    try:
        redis_health = await health_check_redis()
        results["checks"]["redis"] = redis_health
    except HTTPException as e:
        results["checks"]["redis"] = e.detail
        # Redis failure doesn't mark system unhealthy (it's optional)
    
    results["status"] = "healthy" if all_healthy else "degraded"
    
    if not all_healthy:
        raise HTTPException(status_code=503, detail=results)
    
    return results
