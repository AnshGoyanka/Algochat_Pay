"""
Metrics and monitoring endpoints
Provides system metrics for observability
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from typing import Dict, Any
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.user import User
from backend.models.transaction import Transaction, TransactionStatus
from backend.models.fund import Fund
from backend.models.ticket import Ticket
from backend.utils.production_logging import ProductionLogger

router = APIRouter(prefix="/metrics", tags=["Metrics"])
logger = ProductionLogger.get_logger(__name__)


@router.get("")
async def get_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    System metrics overview
    Provides statistics for monitoring dashboard
    """
    try:
        # User metrics
        total_users = db.query(func.count(User.id)).scalar()
        active_users = db.query(func.count(User.id)).filter(
            User.is_active == True
        ).scalar()
        
        # Transaction metrics
        total_transactions = db.query(func.count(Transaction.id)).scalar()
        confirmed_transactions = db.query(func.count(Transaction.id)).filter(
            Transaction.status == TransactionStatus.CONFIRMED
        ).scalar()
        failed_transactions = db.query(func.count(Transaction.id)).filter(
            Transaction.status == TransactionStatus.FAILED
        ).scalar()
        
        # Total volume (ALGO)
        total_volume = db.query(func.sum(Transaction.amount)).filter(
            Transaction.status == TransactionStatus.CONFIRMED
        ).scalar() or 0.0
        
        # Today's stats
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_transactions = db.query(func.count(Transaction.id)).filter(
            Transaction.timestamp >= today_start
        ).scalar()
        
        today_volume = db.query(func.sum(Transaction.amount)).filter(
            Transaction.timestamp >= today_start,
            Transaction.status == TransactionStatus.CONFIRMED
        ).scalar() or 0.0
        
        # Fund metrics
        total_funds = db.query(func.count(Fund.id)).scalar()
        active_funds = db.query(func.count(Fund.id)).filter(
            Fund.is_active == True
        ).scalar()
        funds_goal_met = db.query(func.count(Fund.id)).filter(
            Fund.is_goal_met == True
        ).scalar()
        
        total_fundraised = db.query(func.sum(Fund.current_amount)).scalar() or 0.0
        
        # Ticket metrics
        total_tickets = db.query(func.count(Ticket.id)).scalar()
        valid_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.is_valid == True,
            Ticket.is_used == False
        ).scalar()
        used_tickets = db.query(func.count(Ticket.id)).filter(
            Ticket.is_used == True
        ).scalar()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "users": {
                "total": total_users,
                "active": active_users
            },
            "transactions": {
                "total": total_transactions,
                "confirmed": confirmed_transactions,
                "failed": failed_transactions,
                "success_rate": round(confirmed_transactions / total_transactions * 100, 2) if total_transactions > 0 else 0,
                "today_count": today_transactions,
                "today_volume_algo": round(today_volume, 2)
            },
            "volume": {
                "total_algo": round(total_volume, 2),
                "average_tx_algo": round(total_volume / confirmed_transactions, 2) if confirmed_transactions > 0 else 0
            },
            "fundraising": {
                "total_campaigns": total_funds,
                "active_campaigns": active_funds,
                "successful_campaigns": funds_goal_met,
                "total_raised_algo": round(total_fundraised, 2)
            },
            "tickets": {
                "total_minted": total_tickets,
                "valid_unused": valid_tickets,
                "used": used_tickets
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch metrics: {e}", exc_info=True)
        raise


@router.get("/transactions/recent")
async def get_recent_transactions(
    limit: int = 10,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get recent transactions for monitoring
    """
    try:
        transactions = db.query(Transaction).order_by(
            Transaction.timestamp.desc()
        ).limit(limit).all()
        
        return {
            "count": len(transactions),
            "transactions": [
                {
                    "id": tx.id,
                    "tx_id": tx.tx_id[:16] + "..." if tx.tx_id else None,
                    "type": tx.transaction_type.value if tx.transaction_type else None,
                    "amount": tx.amount,
                    "status": tx.status.value if tx.status else None,
                    "timestamp": tx.timestamp.isoformat() if tx.timestamp else None
                }
                for tx in transactions
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch recent transactions: {e}", exc_info=True)
        raise


@router.get("/performance")
async def get_performance_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Performance metrics for monitoring
    """
    try:
        # Average transaction time (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        recent_txs = db.query(Transaction).filter(
            Transaction.timestamp >= yesterday,
            Transaction.status == TransactionStatus.CONFIRMED,
            Transaction.confirmed_at.isnot(None)
        ).all()
        
        if recent_txs:
            durations = [
                (tx.confirmed_at - tx.timestamp).total_seconds()
                for tx in recent_txs
                if tx.confirmed_at and tx.timestamp
            ]
            
            avg_duration = sum(durations) / len(durations) if durations else 0
            max_duration = max(durations) if durations else 0
            min_duration = min(durations) if durations else 0
        else:
            avg_duration = max_duration = min_duration = 0
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "transaction_performance": {
                "sample_size": len(recent_txs),
                "avg_confirmation_time_sec": round(avg_duration, 2),
                "min_confirmation_time_sec": round(min_duration, 2),
                "max_confirmation_time_sec": round(max_duration, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch performance metrics: {e}", exc_info=True)
        raise
