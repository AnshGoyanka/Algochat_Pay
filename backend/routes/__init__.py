"""
Routes package
"""
from backend.routes.health import router as health_router
from backend.routes.metrics import router as metrics_router
from backend.routes.admin import router as admin_router
from backend.routes.demo import router as demo_router
from backend.routes.demo_freeze import freeze_router

__all__ = ["health_router", "metrics_router", "admin_router", "demo_router", "freeze_router"]
