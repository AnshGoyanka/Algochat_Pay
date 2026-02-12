"""
Performance optimization utilities
Connection pooling, caching, and async improvements
"""
from typing import Optional, Any, Callable
from functools import wraps
import hashlib
import json
import time
from backend.config import settings
from backend.utils.production_logging import ProductionLogger

logger = ProductionLogger.get_logger(__name__)


class CacheManager:
    """
    Simple in-memory cache with TTL support
    Falls back to Redis if available
    """
    
    def __init__(self):
        self._memory_cache = {}
        self._cache_times = {}
        
        # Try to use Redis if available
        if settings.REDIS_ENABLED:
            try:
                import redis
                self.redis_client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True
                )
                self.redis_enabled = True
                logger.info("Cache manager using Redis")
            except Exception as e:
                logger.warning(f"Redis unavailable, using memory cache: {e}")
                self.redis_client = None
                self.redis_enabled = False
        else:
            self.redis_client = None
            self.redis_enabled = False
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments"""
        key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:8]
        return f"{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if self.redis_enabled:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get failed: {e}")
        
        # Fallback to memory cache
        if key in self._memory_cache:
            # Check TTL
            if key in self._cache_times:
                if time.time() < self._cache_times[key]:
                    return self._memory_cache[key]
                else:
                    # Expired
                    del self._memory_cache[key]
                    del self._cache_times[key]
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (seconds)"""
        if self.redis_enabled:
            try:
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value)
                )
                return
            except Exception as e:
                logger.warning(f"Redis set failed: {e}")
        
        # Fallback to memory cache
        self._memory_cache[key] = value
        self._cache_times[key] = time.time() + ttl
    
    def delete(self, key: str):
        """Delete key from cache"""
        if self.redis_enabled:
            try:
                self.redis_client.delete(key)
            except:
                pass
        
        if key in self._memory_cache:
            del self._memory_cache[key]
        if key in self._cache_times:
            del self._cache_times[key]
    
    def clear(self, pattern: Optional[str] = None):
        """Clear cache (optionally by pattern)"""
        if self.redis_enabled and pattern:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
            except:
                pass
        
        if not pattern:
            self._memory_cache.clear()
            self._cache_times.clear()


# Global cache manager
cache_manager = CacheManager()


def cached(ttl: int = 300, prefix: str = "cache"):
    """
    Decorator for caching function results
    
    Usage:
        @cached(ttl=600, prefix="balance")
        def get_balance(address: str):
            return expensive_operation()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {cache_key}")
                return cached_value
            
            # Cache miss - execute function
            logger.debug(f"Cache miss: {cache_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    
    return decorator


class ConnectionPool:
    """
    Database connection pool configuration
    Already handled by SQLAlchemy, but provides tuning parameters
    """
    
    @staticmethod
    def get_pool_config() -> dict:
        """
        Get optimized pool configuration
        
        Returns:
            Dict with SQLAlchemy pool parameters
        """
        if settings.is_production:
            return {
                "pool_size": 20,  # Number of connections to maintain
                "max_overflow": 10,  # Max additional connections
                "pool_recycle": 3600,  # Recycle connections after 1 hour
                "pool_pre_ping": True,  # Test connections before use
                "pool_timeout": 30  # Timeout for getting connection
            }
        else:
            # Development settings
            return {
                "pool_size": 5,
                "max_overflow": 5,
                "pool_recycle": 1800,
                "pool_pre_ping": True,
                "pool_timeout": 10
            }


class BatchProcessor:
    """
    Batch processing utility for bulk operations
    """
    
    @staticmethod
    def batch_list(items: list, batch_size: int = 100):
        """
        Split list into batches
        
        Args:
            items: List to batch
            batch_size: Size of each batch
        
        Yields:
            Batches of items
        """
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
    
    @staticmethod
    async def process_in_batches(
        items: list,
        processor: Callable,
        batch_size: int = 100
    ) -> list:
        """
        Process items in batches
        
        Args:
            items: Items to process
            processor: Async function to process each batch
            batch_size: Batch size
        
        Returns:
            List of all results
        """
        results = []
        
        for batch in BatchProcessor.batch_list(items, batch_size):
            batch_results = await processor(batch)
            results.extend(batch_results)
        
        return results


def optimize_database_query(query):
    """
    Apply common query optimizations
    
    Args:
        query: SQLAlchemy query object
    
    Returns:
        Optimized query
    """
    # Join loading strategies
    from sqlalchemy.orm import joinedload, subqueryload
    
    # You can add specific optimizations here
    # e.g., query.options(joinedload(User.transactions))
    
    return query


class PerformanceMonitor:
    """
    Monitor and log slow operations
    """
    
    def __init__(self, operation_name: str, threshold_ms: float = 1000):
        self.operation_name = operation_name
        self.threshold_ms = threshold_ms
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time() - self.start_time) * 1000
        
        if duration_ms > self.threshold_ms:
            logger.warning(
                f"Slow operation: {self.operation_name}",
                extra={
                    "operation": self.operation_name,
                    "duration_ms": round(duration_ms, 2),
                    "threshold_ms": self.threshold_ms
                }
            )
        else:
            logger.debug(
                f"Operation completed: {self.operation_name}",
                extra={"duration_ms": round(duration_ms, 2)}
            )


# Example usage:
# with PerformanceMonitor("get_balance", threshold_ms=500):
#     balance = algorand_client.get_balance(address)
