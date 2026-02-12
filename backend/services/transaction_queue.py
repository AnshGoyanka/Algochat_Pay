"""
Redis transaction queue for reliable async processing
Ensures transactions are not lost during failures
"""
import json
import redis
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from backend.config import settings
from backend.utils.production_logging import ProductionLogger

logger = ProductionLogger.get_logger(__name__)


class TransactionQueue:
    """
    Redis-based transaction queue
    Provides reliable async transaction processing with retry
    """
    
    def __init__(self):
        if settings.REDIS_ENABLED:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
            self.enabled = True
            logger.info("Transaction queue connected to Redis")
        else:
            self.redis_client = None
            self.enabled = False
            logger.warning("Redis disabled - transaction queue unavailable")
    
    def enqueue_payment(
        self,
        sender_phone: str,
        receiver_phone: str,
        amount: float,
        note: str = "",
        priority: str = "normal"
    ) -> Optional[str]:
        """
        Add payment transaction to queue
        
        Args:
            sender_phone: Sender's phone number
            receiver_phone: Receiver's phone number
            amount: Amount in ALGO
            note: Transaction note
            priority: Priority level ("high", "normal", "low")
        
        Returns:
            Queue ID if successful, None if queue disabled
        """
        if not self.enabled:
            logger.debug("Queue disabled, skipping enqueue")
            return None
        
        try:
            # Create transaction payload
            transaction_data = {
                "type": "payment",
                "sender_phone": sender_phone,
                "receiver_phone": receiver_phone,
                "amount": amount,
                "note": note,
                "priority": priority,
                "enqueued_at": datetime.utcnow().isoformat(),
                "retry_count": 0,
                "max_retries": 5,
                "status": "pending"
            }
            
            # Determine queue based on priority
            queue_name = f"tx_queue:{priority}"
            
            # Add to queue
            queue_id = f"tx:{sender_phone}:{int(datetime.utcnow().timestamp() * 1000)}"
            self.redis_client.rpush(queue_name, json.dumps(transaction_data))
            
            # Store transaction data with ID for tracking
            self.redis_client.setex(
                queue_id,
                timedelta(hours=24),  # Expire after 24 hours
                json.dumps(transaction_data)
            )
            
            logger.info(
                f"Payment enqueued: {queue_id}",
                extra={
                    "sender": sender_phone,
                    "receiver": receiver_phone,
                    "amount": amount,
                    "priority": priority
                }
            )
            
            return queue_id
            
        except Exception as e:
            logger.error(f"Failed to enqueue payment: {e}", exc_info=True)
            return None
    
    def dequeue_payment(self, priority: str = "normal", timeout: int = 5) -> Optional[Dict[str, Any]]:
        """
        Get next payment from queue (blocking with timeout)
        
        Args:
            priority: Queue priority to read from
            timeout: Timeout in seconds (0 for non-blocking)
        
        Returns:
            Transaction data dict or None
        """
        if not self.enabled:
            return None
        
        try:
            queue_name = f"tx_queue:{priority}"
            
            if timeout > 0:
                # Blocking pop with timeout
                result = self.redis_client.blpop(queue_name, timeout=timeout)
            else:
                # Non-blocking pop
                result = self.redis_client.lpop(queue_name)
            
            if result:
                # blpop returns (key, value), lpop returns value
                data_str = result[1] if timeout > 0 else result
                transaction_data = json.loads(data_str)
                
                logger.info(
                    f"Payment dequeued from {priority} queue",
                    extra={"transaction": transaction_data}
                )
                
                return transaction_data
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to dequeue payment: {e}", exc_info=True)
            return None
    
    def enqueue_failed_transaction(
        self,
        transaction_data: Dict[str, Any],
        error_message: str
    ):
        """
        Re-queue failed transaction for retry
        
        Args:
            transaction_data: Original transaction data
            error_message: Error message from failure
        """
        if not self.enabled:
            return
        
        try:
            # Increment retry count
            retry_count = transaction_data.get("retry_count", 0) + 1
            max_retries = transaction_data.get("max_retries", 5)
            
            if retry_count > max_retries:
                logger.error(
                    f"Transaction exceeded max retries ({max_retries})",
                    extra={"transaction": transaction_data}
                )
                
                # Move to dead letter queue
                self._move_to_dead_letter_queue(transaction_data, error_message)
                return
            
            # Update transaction data
            transaction_data["retry_count"] = retry_count
            transaction_data["last_error"] = error_message
            transaction_data["last_retry_at"] = datetime.utcnow().isoformat()
            transaction_data["status"] = "retrying"
            
            # Calculate backoff delay (exponential: 5s, 10s, 20s, 40s, 80s)
            delay_seconds = min(5 * (2 ** (retry_count - 1)), 300)  # Max 5 minutes
            
            # Add to retry queue with delay
            retry_queue = f"tx_queue:retry:{delay_seconds}"
            self.redis_client.rpush(retry_queue, json.dumps(transaction_data))
            
            logger.info(
                f"Transaction re-queued for retry {retry_count}/{max_retries}",
                extra={
                    "transaction": transaction_data,
                    "delay": delay_seconds
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to re-queue transaction: {e}", exc_info=True)
    
    def _move_to_dead_letter_queue(
        self,
        transaction_data: Dict[str, Any],
        final_error: str
    ):
        """
        Move permanently failed transaction to dead letter queue
        
        Args:
            transaction_data: Transaction data
            final_error: Final error message
        """
        try:
            transaction_data["status"] = "failed_permanently"
            transaction_data["final_error"] = final_error
            transaction_data["moved_to_dlq_at"] = datetime.utcnow().isoformat()
            
            # Add to DLQ (kept for 7 days for manual investigation)
            dlq_key = f"tx_dlq:{transaction_data.get('sender_phone')}:{int(datetime.utcnow().timestamp())}"
            self.redis_client.setex(
                dlq_key,
                timedelta(days=7),
                json.dumps(transaction_data)
            )
            
            logger.error(
                "Transaction moved to dead letter queue",
                extra={"transaction": transaction_data, "error": final_error}
            )
            
        except Exception as e:
            logger.error(f"Failed to move to DLQ: {e}", exc_info=True)
    
    def get_queue_stats(self) -> Dict[str, Any]:
        """
        Get statistics about queue lengths
        
        Returns:
            Dict with queue statistics
        """
        if not self.enabled:
            return {"enabled": False}
        
        try:
            stats = {
                "enabled": True,
                "queues": {}
            }
            
            for priority in ["high", "normal", "low"]:
                queue_name = f"tx_queue:{priority}"
                length = self.redis_client.llen(queue_name)
                stats["queues"][priority] = length
            
            # Count retry queues
            retry_keys = self.redis_client.keys("tx_queue:retry:*")
            stats["retry_queues"] = len(retry_keys)
            
            # Count DLQ items
            dlq_keys = self.redis_client.keys("tx_dlq:*")
            stats["dead_letter_queue"] = len(dlq_keys)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get queue stats: {e}", exc_info=True)
            return {"enabled": True, "error": str(e)}
    
    def clear_queue(self, queue_name: str = "all"):
        """
        Clear queue(s) - for testing/admin use
        
        Args:
            queue_name: Queue to clear ("all", "high", "normal", "low", "retry", "dlq")
        """
        if not self.enabled:
            return
        
        try:
            if queue_name == "all":
                patterns = [
                    "tx_queue:*",
                    "tx_dlq:*"
                ]
            elif queue_name == "dlq":
                patterns = ["tx_dlq:*"]
            elif queue_name == "retry":
                patterns = ["tx_queue:retry:*"]
            else:
                patterns = [f"tx_queue:{queue_name}"]
            
            for pattern in patterns:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} keys matching {pattern}")
            
        except Exception as e:
            logger.error(f"Failed to clear queue: {e}", exc_info=True)


# Global transaction queue instance
transaction_queue = TransactionQueue()
