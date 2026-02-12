"""
FastAPI middleware for logging and correlation ID tracking
"""
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import uuid

from backend.utils.production_logging import ProductionLogger, performance_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request/response logging
    Adds correlation ID to all requests
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = ProductionLogger.get_logger("http")
    
    async def dispatch(self, request: Request, call_next):
        # Generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        ProductionLogger.set_correlation_id(correlation_id)
        
        # Start timing
        start_time = time.time()
        
        # Log incoming request
        self.logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown")
            }
        )
        
        # Process request
        try:
            response: Response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            self.logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms
                }
            )
            
            # Track performance
            performance_logger.log_duration(
                f"{request.method} {request.url.path}",
                duration_ms
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            self.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "duration_ms": duration_ms
                },
                exc_info=True
            )
            raise
        finally:
            # Clear correlation ID
            ProductionLogger.clear_correlation_id()


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for security event logging
    Tracks suspicious activities
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = ProductionLogger.get_logger("security")
    
    async def dispatch(self, request: Request, call_next):
        # Check for suspicious patterns
        suspicious = False
        reasons = []
        
        # Check for SQL injection attempts
        path = str(request.url.path).lower()
        if any(pattern in path for pattern in ["select ", "union ", "drop ", "insert "]):
            suspicious = True
            reasons.append("sql_injection_attempt")
        
        # Check for path traversal
        if ".." in path or "%2e%2e" in path:
            suspicious = True
            reasons.append("path_traversal_attempt")
        
        # Log suspicious activity
        if suspicious:
            self.logger.warning(
                "Suspicious request detected",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host if request.client else "unknown",
                    "reasons": reasons
                }
            )
        
        return await call_next(request)
