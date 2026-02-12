"""
Production-grade structured logging system
Adds correlation IDs, JSON formatting, and contextual logging
"""
import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from contextvars import ContextVar
import uuid

from pythonjsonlogger import jsonlogger

# Context variable for correlation ID (request tracking)
correlation_id: ContextVar[str] = ContextVar('correlation_id', default='')


class CorrelationIdFilter(logging.Filter):
    """Add correlation ID to all log records"""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id.get() or 'no-correlation-id'
        return True


class SensitiveDataFilter(logging.Filter):
    """Filter out sensitive data from logs"""
    
    SENSITIVE_KEYS = {
        'private_key', 'mnemonic', 'password', 'secret', 'token',
        'encrypted_private_key', 'api_key', 'auth_token'
    }
    
    def filter(self, record: logging.LogRecord) -> bool:
        # Check message for sensitive data
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            msg_lower = record.msg.lower()
            for key in self.SENSITIVE_KEYS:
                if key in msg_lower:
                    # Don't block, but sanitize
                    record.msg = self._sanitize_message(record.msg)
        return True
    
    def _sanitize_message(self, msg: str) -> str:
        """Replace potential sensitive values with [REDACTED]"""
        # Simple sanitization - replace long alphanumeric strings
        import re
        return re.sub(r'[A-Za-z0-9]{32,}', '[REDACTED]', msg)


class ProductionLogger:
    """
    Production-grade logger factory
    
    Features:
    - Structured JSON logging
    - Correlation ID tracking
    - Sensitive data filtering
    - Multiple output handlers
    - Log level per environment
    """
    
    _configured = False
    _loggers: Dict[str, logging.Logger] = {}
    
    @classmethod
    def setup(
        cls,
        log_level: str = "INFO",
        log_file: str = "logs/algochat.log",
        enable_json: bool = True
    ):
        """
        Setup production logging system
        
        Args:
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
            log_file: Path to log file
            enable_json: Use JSON formatter for structured logs
        """
        if cls._configured:
            return
        
        # Create logs directory
        log_path = Path(log_file)
        log_path.parent.mkdir(exist_ok=True)
        
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Console handler (human-readable for development)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s [%(correlation_id)s] %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        console_handler.addFilter(CorrelationIdFilter())
        console_handler.addFilter(SensitiveDataFilter())
        
        # File handler (JSON formatted for log aggregation)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        if enable_json:
            json_format = jsonlogger.JsonFormatter(
                '%(asctime)s %(name)s %(levelname)s %(correlation_id)s %(message)s %(pathname)s %(lineno)d'
            )
            file_handler.setFormatter(json_format)
        else:
            file_handler.setFormatter(console_format)
        
        file_handler.addFilter(CorrelationIdFilter())
        file_handler.addFilter(SensitiveDataFilter())
        
        # Add handlers to root logger
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        cls._configured = True
        
        # Log system startup
        logger = cls.get_logger("system")
        logger.info("Production logging system initialized", extra={
            "log_level": log_level,
            "log_file": log_file,
            "json_enabled": enable_json
        })
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create logger for module"""
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
        return cls._loggers[name]
    
    @classmethod
    def set_correlation_id(cls, corr_id: Optional[str] = None):
        """Set correlation ID for request tracking"""
        correlation_id.set(corr_id or str(uuid.uuid4()))
    
    @classmethod
    def get_correlation_id(cls) -> str:
        """Get current correlation ID"""
        return correlation_id.get()
    
    @classmethod
    def clear_correlation_id(cls):
        """Clear correlation ID"""
        correlation_id.set('')


class EventLogger:
    """
    Specialized logger for business events
    Tracks key system events for analytics and debugging
    """
    
    def __init__(self):
        self.logger = ProductionLogger.get_logger("events")
    
    def wallet_created(self, phone: str, address: str, **kwargs):
        """Log wallet creation event"""
        self.logger.info(
            "Wallet created",
            extra={
                "event_type": "wallet_created",
                "phone": self._mask_phone(phone),
                "wallet_address": address[:10] + "...",
                **kwargs
            }
        )
    
    def transaction_initiated(self, tx_type: str, amount: float, **kwargs):
        """Log transaction start"""
        self.logger.info(
            f"Transaction initiated: {tx_type}",
            extra={
                "event_type": "transaction_initiated",
                "tx_type": tx_type,
                "amount": amount,
                **kwargs
            }
        )
    
    def transaction_completed(self, tx_id: str, duration_ms: float, **kwargs):
        """Log transaction completion"""
        self.logger.info(
            "Transaction completed",
            extra={
                "event_type": "transaction_completed",
                "tx_id": tx_id[:16] + "...",
                "duration_ms": duration_ms,
                **kwargs
            }
        )
    
    def transaction_failed(self, error: str, **kwargs):
        """Log transaction failure"""
        self.logger.error(
            f"Transaction failed: {error}",
            extra={
                "event_type": "transaction_failed",
                "error": error,
                **kwargs
            }
        )
    
    def command_received(self, phone: str, command: str, **kwargs):
        """Log WhatsApp command"""
        self.logger.info(
            f"Command received: {command}",
            extra={
                "event_type": "command_received",
                "phone": self._mask_phone(phone),
                "command_type": command,
                **kwargs
            }
        )
    
    def smart_contract_call(self, contract_type: str, app_id: int, **kwargs):
        """Log smart contract interaction"""
        self.logger.info(
            f"Smart contract call: {contract_type}",
            extra={
                "event_type": "smart_contract_call",
                "contract_type": contract_type,
                "app_id": app_id,
                **kwargs
            }
        )
    
    def security_event(self, event: str, severity: str, **kwargs):
        """Log security-related events"""
        log_func = self.logger.warning if severity == "medium" else self.logger.error
        log_func(
            f"Security event: {event}",
            extra={
                "event_type": "security_event",
                "security_event": event,
                "severity": severity,
                **kwargs
            }
        )
    
    @staticmethod
    def _mask_phone(phone: str) -> str:
        """Mask phone number for privacy"""
        if len(phone) > 6:
            return phone[:3] + "****" + phone[-3:]
        return "***"


# Global event logger instance
event_logger = EventLogger()


class PerformanceLogger:
    """Track performance metrics"""
    
    def __init__(self):
        self.logger = ProductionLogger.get_logger("performance")
    
    def log_duration(self, operation: str, duration_ms: float, **kwargs):
        """Log operation duration"""
        level = logging.WARNING if duration_ms > 5000 else logging.INFO
        self.logger.log(
            level,
            f"{operation} completed in {duration_ms:.2f}ms",
            extra={
                "operation": operation,
                "duration_ms": duration_ms,
                **kwargs
            }
        )


# Global performance logger
performance_logger = PerformanceLogger()
