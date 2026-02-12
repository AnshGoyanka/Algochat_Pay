"""
Demo safety utilities
Provides retry logic and fallback mechanisms for reliable demo execution
"""
import time
from typing import Callable, Optional, Any, TypeVar, List
from functools import wraps

from backend.utils.production_logging import ProductionLogger, event_logger

logger = ProductionLogger.get_logger(__name__)

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 0.5,
        max_delay: float = 5.0,
        exponential_base: float = 2.0,
        exceptions: tuple = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.exceptions = exceptions
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt with exponential backoff"""
        delay = self.initial_delay * (self.exponential_base ** (attempt - 1))
        return min(delay, self.max_delay)


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator for automatic retry with exponential backoff
    
    Usage:
        @with_retry(RetryConfig(max_attempts=3, initial_delay=1.0))
        async def risky_operation():
            # code that might fail
            pass
    """
    if config is None:
        config = RetryConfig()
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    result = await func(*args, **kwargs)
                    
                    # Log success after failure recovery
                    if attempt > 1:
                        logger.info(
                            f"Operation succeeded on attempt {attempt}/{config.max_attempts}",
                            extra={"function": func.__name__, "attempt": attempt}
                        )
                    
                    return result
                    
                except config.exceptions as e:
                    last_exception = e
                    
                    # Log the failure
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed: {e}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "error": str(e)
                        }
                    )
                    
                    # Don't sleep after last attempt
                    if attempt < config.max_attempts:
                        delay = config.calculate_delay(attempt)
                        logger.debug(f"Retrying in {delay}s...")
                        time.sleep(delay)
            
            # All attempts exhausted
            logger.error(
                f"All {config.max_attempts} attempts failed",
                extra={
                    "function": func.__name__,
                    "final_error": str(last_exception)
                }
            )
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(1, config.max_attempts + 1):
                try:
                    result = func(*args, **kwargs)
                    
                    if attempt > 1:
                        logger.info(
                            f"Operation succeeded on attempt {attempt}/{config.max_attempts}",
                            extra={"function": func.__name__, "attempt": attempt}
                        )
                    
                    return result
                    
                except config.exceptions as e:
                    last_exception = e
                    
                    logger.warning(
                        f"Attempt {attempt}/{config.max_attempts} failed: {e}",
                        extra={
                            "function": func.__name__,
                            "attempt": attempt,
                            "error": str(e)
                        }
                    )
                    
                    if attempt < config.max_attempts:
                        delay = config.calculate_delay(attempt)
                        logger.debug(f"Retrying in {delay}s...")
                        time.sleep(delay)
            
            logger.error(
                f"All {config.max_attempts} attempts failed",
                extra={
                    "function": func.__name__,
                    "final_error": str(last_exception)
                }
            )
            raise last_exception
        
        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


class AlgorandNodeFallback:
    """
    Manages fallback between multiple Algorand nodes
    Ensures demo reliability by switching to backup nodes on failure
    """
    
    def __init__(self, primary_node: str, backup_nodes: Optional[List[str]] = None):
        self.primary_node = primary_node
        self.backup_nodes = backup_nodes or []
        self.all_nodes = [primary_node] + self.backup_nodes
        self.current_node_index = 0
        self.failure_counts = {node: 0 for node in self.all_nodes}
        self.max_failures_before_switch = 2
    
    @property
    def current_node(self) -> str:
        """Get currently active node"""
        return self.all_nodes[self.current_node_index]
    
    def record_success(self):
        """Record successful operation on current node"""
        node = self.current_node
        self.failure_counts[node] = 0
        logger.debug(f"Node {node} operation successful")
    
    def record_failure(self):
        """
        Record failure on current node
        Switch to backup if threshold exceeded
        """
        node = self.current_node
        self.failure_counts[node] += 1
        
        logger.warning(
            f"Node {node} failure count: {self.failure_counts[node]}",
            extra={"node": node, "failures": self.failure_counts[node]}
        )
        
        # Switch to backup node if threshold exceeded
        if self.failure_counts[node] >= self.max_failures_before_switch:
            self._switch_to_backup()
    
    def _switch_to_backup(self):
        """Switch to next backup node"""
        old_node = self.current_node
        old_index = self.current_node_index
        
        # Try next node
        self.current_node_index = (self.current_node_index + 1) % len(self.all_nodes)
        new_node = self.current_node
        
        # If we've cycled through all nodes, reset failure counts
        if self.current_node_index <= old_index:
            logger.warning("Cycled through all nodes, resetting failure counts")
            self.failure_counts = {node: 0 for node in self.all_nodes}
        
        logger.warning(
            f"Switching from {old_node} to {new_node}",
            extra={"old_node": old_node, "new_node": new_node}
        )
        
        event_logger.security_event(
            "node_failover",
            {"from": old_node, "to": new_node}
        )
    
    def get_node_with_retry(self) -> str:
        """
        Get a working node with automatic fallback
        This should be called before each Algorand operation
        """
        return self.current_node


class CircuitBreaker:
    """
    Circuit breaker pattern for failing fast during outages
    Prevents cascading failures during demo
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = "closed"  # closed, open, half-open
    
    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection"""
        
        # Check if we should attempt recovery
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half-open"
                logger.info("Circuit breaker entering half-open state")
            else:
                raise Exception(
                    f"Circuit breaker is OPEN. Service unavailable. "
                    f"Retry after {self.recovery_timeout}s"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt recovery"""
        if self.last_failure_time is None:
            return True
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful operation"""
        if self.state == "half-open":
            logger.info("Circuit breaker recovered, closing circuit")
            self.state = "closed"
        
        self.failure_count = 0
        self.last_failure_time = None
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.error(
                f"Circuit breaker opened after {self.failure_count} failures",
                extra={"failure_count": self.failure_count}
            )
            event_logger.security_event(
                "circuit_breaker_open",
                {"failure_count": self.failure_count}
            )


def safe_demo_operation(operation_name: str):
    """
    Wrapper for critical demo operations
    Combines retry logic with informative error messages
    
    Usage:
        @safe_demo_operation("wallet_creation")
        async def create_wallet(phone_number):
            # implementation
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        # Apply retry logic
        retry_config = RetryConfig(
            max_attempts=3,
            initial_delay=1.0,
            max_delay=5.0
        )
        
        @with_retry(retry_config)
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            try:
                event_logger.command_received(operation_name, {"args": str(args)[:100]})
                result = await func(*args, **kwargs)
                logger.info(f"Demo operation '{operation_name}' completed successfully")
                return result
            except Exception as e:
                logger.error(
                    f"Demo operation '{operation_name}' failed after retries",
                    extra={"operation": operation_name, "error": str(e)},
                    exc_info=True
                )
                raise
        
        @with_retry(retry_config)
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            try:
                event_logger.command_received(operation_name, {"args": str(args)[:100]})
                result = func(*args, **kwargs)
                logger.info(f"Demo operation '{operation_name}' completed successfully")
                return result
            except Exception as e:
                logger.error(
                    f"Demo operation '{operation_name}' failed after retries",
                    extra={"operation": operation_name, "error": str(e)},
                    exc_info=True
                )
                raise
        
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
