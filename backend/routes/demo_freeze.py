"""
Demo Freeze API Endpoint
Control freeze mode via API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from backend.database import get_db
from backend.services.demo_metrics_service import DemoMetricsService
from backend.services.demo_freeze_service import DemoFreezeManager
from backend.utils.production_logging import ProductionLogger

logger = ProductionLogger.get_logger(__name__)

freeze_router = APIRouter(prefix="/demo/freeze", tags=["Demo Freeze"])


@freeze_router.get("/status", response_model=Dict[str, Any])
async def get_freeze_status() -> Dict[str, Any]:
    """
    GET /demo/freeze/status
    
    Check current freeze status
    
    Returns:
        {
            "is_frozen": bool,
            "has_cache": bool,
            "frozen_at": str or null,
            "cache_age_seconds": float or null
        }
    """
    try:
        status = DemoFreezeManager.get_freeze_status()
        logger.info("Freeze status retrieved", extra=status)
        return status
        
    except Exception as e:
        logger.error(f"Failed to get freeze status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to get freeze status")


@freeze_router.post("/freeze", response_model=Dict[str, str])
async def freeze_metrics(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    POST /demo/freeze/freeze
    
    Freeze current metrics for consistent presentations
    
    Returns:
        {
            "status": "success",
            "message": "Metrics frozen",
            "frozen_at": "2026-05-15T10:30:00"
        }
    """
    try:
        # Get current metrics
        metrics_service = DemoMetricsService(db)
        metrics = metrics_service.get_comprehensive_demo_metrics()
        
        # Freeze them
        DemoFreezeManager.freeze_metrics(metrics)
        
        logger.info("Demo metrics frozen via API")
        
        return {
            "status": "success",
            "message": "Metrics frozen successfully",
            "frozen_at": metrics['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Failed to freeze metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to freeze metrics")


@freeze_router.post("/unfreeze", response_model=Dict[str, str])
async def unfreeze_metrics() -> Dict[str, str]:
    """
    POST /demo/freeze/unfreeze
    
    Unfreeze metrics to serve live data
    
    Returns:
        {
            "status": "success",
            "message": "Metrics unfrozen"
        }
    """
    try:
        unfrozen = DemoFreezeManager.unfreeze()
        
        if unfrozen:
            logger.info("Demo metrics unfrozen via API")
            return {
                "status": "success",
                "message": "Metrics unfrozen, now serving live data"
            }
        else:
            logger.warning("Attempted to unfreeze but no cache existed")
            return {
                "status": "warning",
                "message": "No frozen metrics found, already serving live data"
            }
        
    except Exception as e:
        logger.error(f"Failed to unfreeze metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to unfreeze metrics")
