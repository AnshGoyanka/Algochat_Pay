"""
Demo Freeze Service
Locks metrics during live presentations so numbers stay consistent
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from backend.utils.production_logging import ProductionLogger

logger = ProductionLogger.get_logger(__name__)


class DemoFreezeManager:
    """
    Manages frozen demo metrics for presentations
    
    When DEMO_FREEZE=true, metrics are cached and served consistently
    Perfect for judge presentations where changing numbers would be confusing
    """
    
    FREEZE_FILE = Path("data/demo_freeze_cache.json")
    
    @classmethod
    def is_frozen(cls) -> bool:
        """Check if demo is in freeze mode"""
        return os.getenv("DEMO_FREEZE", "false").lower() in ["true", "1", "yes"]
    
    @classmethod
    def freeze_metrics(cls, metrics: Dict[str, Any]) -> None:
        """
        Freeze current metrics to file
        
        Args:
            metrics: The metrics dictionary to freeze
        """
        cls.FREEZE_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        frozen_data = {
            "frozen_at": datetime.utcnow().isoformat(),
            "frozen_by": "demo_freeze_service",
            "metrics": metrics
        }
        
        with open(cls.FREEZE_FILE, 'w') as f:
            json.dump(frozen_data, f, indent=2)
        
        logger.info("Demo metrics frozen", extra={
            "frozen_at": frozen_data["frozen_at"],
            "metrics_keys": list(metrics.keys())
        })
    
    @classmethod
    def get_frozen_metrics(cls) -> Optional[Dict[str, Any]]:
        """
        Get frozen metrics if they exist
        
        Returns:
            Frozen metrics dict or None if not frozen
        """
        if not cls.FREEZE_FILE.exists():
            return None
        
        try:
            with open(cls.FREEZE_FILE, 'r') as f:
                frozen_data = json.load(f)
            
            logger.debug("Retrieved frozen metrics", extra={
                "frozen_at": frozen_data.get("frozen_at"),
                "age_seconds": (
                    datetime.utcnow() - datetime.fromisoformat(frozen_data.get("frozen_at"))
                ).total_seconds()
            })
            
            return frozen_data.get("metrics")
            
        except Exception as e:
            logger.error(f"Failed to load frozen metrics: {str(e)}", exc_info=True)
            return None
    
    @classmethod
    def unfreeze(cls) -> bool:
        """
        Remove frozen metrics
        
        Returns:
            True if unfrozen, False if no freeze file existed
        """
        if cls.FREEZE_FILE.exists():
            cls.FREEZE_FILE.unlink()
            logger.info("Demo metrics unfrozen")
            return True
        else:
            logger.warning("Attempted to unfreeze but no freeze file exists")
            return False
    
    @classmethod
    def get_freeze_status(cls) -> Dict[str, Any]:
        """
        Get current freeze status
        
        Returns:
            {
                "is_frozen": bool,
                "frozen_at": str or None,
                "cache_age_seconds": float or None
            }
        """
        is_frozen = cls.is_frozen()
        frozen_metrics = cls.get_frozen_metrics()
        
        if frozen_metrics and cls.FREEZE_FILE.exists():
            try:
                with open(cls.FREEZE_FILE, 'r') as f:
                    freeze_data = json.load(f)
                
                frozen_at = freeze_data.get("frozen_at")
                cache_age = (
                    datetime.utcnow() - datetime.fromisoformat(frozen_at)
                ).total_seconds() if frozen_at else None
                
                return {
                    "is_frozen": is_frozen,
                    "has_cache": True,
                    "frozen_at": frozen_at,
                    "cache_age_seconds": cache_age
                }
            except Exception as e:
                logger.error(f"Error reading freeze status: {str(e)}")
                return {
                    "is_frozen": is_frozen,
                    "has_cache": False,
                    "frozen_at": None,
                    "cache_age_seconds": None
                }
        else:
            return {
                "is_frozen": is_frozen,
                "has_cache": False,
                "frozen_at": None,
                "cache_age_seconds": None
            }


def with_freeze_support(func):
    """
    Decorator to add freeze mode support to metrics functions
    
    Usage:
        @with_freeze_support
        def get_metrics(db: Session) -> Dict:
            # ... calculate metrics
            return metrics
    
    When DEMO_FREEZE=true, returns cached metrics instead
    """
    def wrapper(*args, **kwargs):
        freeze_mgr = DemoFreezeManager()
        
        if freeze_mgr.is_frozen():
            cached = freeze_mgr.get_frozen_metrics()
            
            if cached:
                logger.info(f"Serving frozen metrics for {func.__name__}")
                return cached
            else:
                logger.warning(
                    f"DEMO_FREEZE enabled but no cache exists, falling back to live metrics"
                )
        
        # Not frozen or no cache - calculate live
        result = func(*args, **kwargs)
        return result
    
    return wrapper
