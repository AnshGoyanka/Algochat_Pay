"""
Security middleware and utilities
Rate limiting, input validation, and security hardening
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional
import time
import re
from collections import defaultdict
from datetime import datetime, timedelta

from backend.config import settings
from backend.utils.production_logging import ProductionLogger, event_logger

logger = ProductionLogger.get_logger(__name__)


class RateLimiter:
    """
    Rate limiter using sliding window algorithm
    Tracks requests per phone number/IP address
    """
    
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed under rate limit
        
        Args:
            identifier: Phone number or IP address
        
        Returns:
            True if allowed, False if rate limited
        """
        now = time.time()
        window_start = now - self.window_seconds
        
        # Remove old requests outside window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > window_start
        ]
        
        # Check if within limit
        if len(self.requests[identifier]) >= self.max_requests:
            logger.warning(
                f"Rate limit exceeded for {identifier}",
                extra={"identifier": identifier, "count": len(self.requests[identifier])}
            )
            event_logger.security_event(
                "rate_limit_exceeded",
                {"identifier": identifier, "requests": len(self.requests[identifier])}
            )
            return False
        
        # Add current request
        self.requests[identifier].append(now)
        return True
    
    def reset(self, identifier: str):
        """Reset rate limit for identifier"""
        if identifier in self.requests:
            del self.requests[identifier]


# Global rate limiter instances
phone_rate_limiter = RateLimiter(
    max_requests=settings.RATE_LIMIT_PER_MINUTE,
    window_seconds=60
)

ip_rate_limiter = RateLimiter(
    max_requests=settings.RATE_LIMIT_PER_MINUTE * 3,  # More lenient for IP
    window_seconds=60
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting
    Applies to all endpoints
    """
    
    async def dispatch(self, request: Request, call_next):
        if not settings.RATE_LIMIT_ENABLED:
            return await call_next(request)
        
        # Get identifier (prefer phone from body, fallback to IP)
        identifier = request.client.host if request.client else "unknown"
        
        # Try to get phone number from request body for better tracking
        if request.method == "POST":
            try:
                # Don't consume the body, just peek
                body = await request.body()
                request._body = body  # Store for later use
                
                # Simple regex to find phone numbers
                phone_match = re.search(r'"phone[_]?number":\s*"(\+?\d+)"', body.decode())
                if phone_match:
                    identifier = phone_match.group(1)
            except:
                pass
        
        # Check rate limit
        if not ip_rate_limiter.is_allowed(identifier):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60
                }
            )
        
        response = await call_next(request)
        return response


class CommandInjectionValidator:
    """
    Validates user input for command injection attempts
    Protects against malicious commands in WhatsApp messages
    """
    
    # Dangerous patterns
    INJECTION_PATTERNS = [
        r'[;&|`$()]',  # Shell metacharacters
        r'\.\./',  # Path traversal
        r'<script',  # XSS attempts
        r'union.*select',  # SQL injection (basic)
        r'drop\s+table',  # SQL injection
        r'exec\s*\(',  # Code execution
        r'eval\s*\(',  # Code execution
        r'__import__',  # Python imports
        r'subprocess',  # System commands
        r'os\.',  # OS module access
    ]
    
    @classmethod
    def is_safe(cls, user_input: str) -> bool:
        """
        Check if input is safe from injection attacks
        
        Args:
            user_input: Raw user input string
        
        Returns:
            True if safe, False if potentially malicious
        """
        input_lower = user_input.lower()
        
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, input_lower):
                logger.warning(
                    f"Potential injection detected: {pattern}",
                    extra={"pattern": pattern, "input": user_input[:50]}
                )
                event_logger.security_event(
                    "injection_attempt",
                    {"pattern": pattern, "input_preview": user_input[:50]}
                )
                return False
        
        return True
    
    @classmethod
    def sanitize(cls, user_input: str) -> str:
        """
        Sanitize input by removing dangerous characters
        
        Args:
            user_input: Raw input
        
        Returns:
            Sanitized string
        """
        # Remove shell metacharacters
        sanitized = re.sub(r'[;&|`$()]', '', user_input)
        
        # Remove path traversal attempts
        sanitized = sanitized.replace('../', '').replace('..\\', '')
        
        return sanitized


class TransactionLimits:
    """
    Enforces transaction limits for security
    Prevents large unauthorized transfers
    """
    
    # Default limits (can be customized per user tier)
    MAX_TRANSACTION_AMOUNT = 100.0  # ALGO
    MAX_DAILY_AMOUNT = 500.0  # ALGO
    MAX_TRANSACTIONS_PER_DAY = 20
    
    def __init__(self):
        self.daily_totals: Dict[str, float] = defaultdict(float)
        self.daily_counts: Dict[str, int] = defaultdict(int)
        self.last_reset = datetime.utcnow().date()
    
    def check_limits(self, phone_number: str, amount: float) -> tuple[bool, Optional[str]]:
        """
        Check if transaction is within limits
        
        Args:
            phone_number: User identifier
            amount: Transaction amount in ALGO
        
        Returns:
            (allowed, error_message)
        """
        # Reset daily limits if new day
        current_date = datetime.utcnow().date()
        if current_date > self.last_reset:
            self.daily_totals.clear()
            self.daily_counts.clear()
            self.last_reset = current_date
        
        # Check single transaction limit
        if amount > self.MAX_TRANSACTION_AMOUNT:
            error = f"Transaction amount exceeds limit of {self.MAX_TRANSACTION_AMOUNT} ALGO"
            logger.warning(
                f"Transaction limit exceeded: {amount} ALGO",
                extra={"phone": phone_number, "amount": amount}
            )
            event_logger.security_event(
                "transaction_limit_exceeded",
                {"phone": phone_number, "amount": amount, "limit": self.MAX_TRANSACTION_AMOUNT}
            )
            return False, error
        
        # Check daily amount limit
        current_daily_total = self.daily_totals[phone_number]
        if current_daily_total + amount > self.MAX_DAILY_AMOUNT:
            error = f"Daily transaction limit exceeded. Limit: {self.MAX_DAILY_AMOUNT} ALGO"
            logger.warning(
                f"Daily amount limit exceeded",
                extra={"phone": phone_number, "current": current_daily_total, "attempted": amount}
            )
            event_logger.security_event(
                "daily_limit_exceeded",
                {"phone": phone_number, "current": current_daily_total, "attempted": amount}
            )
            return False, error
        
        # Check daily transaction count
        current_count = self.daily_counts[phone_number]
        if current_count >= self.MAX_TRANSACTIONS_PER_DAY:
            error = f"Daily transaction count exceeded. Limit: {self.MAX_TRANSACTIONS_PER_DAY}"
            logger.warning(
                f"Transaction count limit exceeded",
                extra={"phone": phone_number, "count": current_count}
            )
            return False, error
        
        # Update counters
        self.daily_totals[phone_number] += amount
        self.daily_counts[phone_number] += 1
        
        return True, None


# Global transaction limits
transaction_limits = TransactionLimits()


def validate_algorand_address(address: str) -> bool:
    """
    Validate Algorand address format
    
    Args:
        address: Algorand address string
    
    Returns:
        True if valid format
    """
    # Algorand addresses are 58 characters, base32 encoded
    if len(address) != 58:
        return False
    
    # Check if it's base32 (A-Z, 2-7)
    if not re.match(r'^[A-Z2-7]{58}$', address):
        return False
    
    return True


def validate_phone_number_format(phone: str) -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number string
    
    Returns:
        True if valid format
    """
    # Must start with + and contain 10-15 digits
    if not re.match(r'^\+\d{10,15}$', phone):
        return False
    
    return True


def validate_amount(amount: float) -> tuple[bool, Optional[str]]:
    """
    Validate transaction amount
    
    Args:
        amount: Amount in ALGO
    
    Returns:
        (valid, error_message)
    """
    if amount <= 0:
        return False, "Amount must be positive"
    
    if amount < 0.001:
        return False, "Amount too small. Minimum: 0.001 ALGO"
    
    if amount > 1000000:
        return False, "Amount too large"
    
    # Check for reasonable decimal places (max 6 for microALGOs)
    if len(str(amount).split('.')[-1]) > 6:
        return False, "Too many decimal places. Max: 6"
    
    return True, None
