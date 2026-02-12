"""
Admin dashboard API endpoints
Provides system overview and management capabilities
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from backend.database import get_db
from backend.models.user import User
from backend.models.transaction import Transaction, TransactionStatus
from backend.models.fund import Fund
from backend.models.ticket import Ticket
from backend.models.audit_log import AuditLog
from backend.services.transaction_queue import transaction_queue
from backend.utils.production_logging import ProductionLogger

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = ProductionLogger.get_logger(__name__)


@router.get("/dashboard")
async def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Admin dashboard overview
    Provides key metrics and insights
    """
    try:
        # Time ranges
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_ago = now - timedelta(days=7)
        
        # User stats
        total_users = db.query(func.count(User.id)).scalar()
        new_users_today = db.query(func.count(User.id)).filter(
            User.created_at >= today_start
        ).scalar()
        new_users_week = db.query(func.count(User.id)).filter(
            User.created_at >= week_ago
        ).scalar()
        
        # Transaction stats
        total_txs = db.query(func.count(Transaction.id)).scalar()
        confirmed_txs = db.query(func.count(Transaction.id)).filter(
            Transaction.status == TransactionStatus.CONFIRMED
        ).scalar()
        failed_txs = db.query(func.count(Transaction.id)).filter(
            Transaction.status == TransactionStatus.FAILED
        ).scalar()
        pending_txs = db.query(func.count(Transaction.id)).filter(
            Transaction.status == TransactionStatus.PENDING
        ).scalar()
        
        # Volume stats
        total_volume = db.query(func.sum(Transaction.amount)).filter(
            Transaction.status == TransactionStatus.CONFIRMED
        ).scalar() or 0.0
        
        today_volume = db.query(func.sum(Transaction.amount)).filter(
            Transaction.timestamp >= today_start,
            Transaction.status == TransactionStatus.CONFIRMED
        ).scalar() or 0.0
        
        # Fund stats
        active_funds = db.query(func.count(Fund.id)).filter(
            Fund.is_active == True
        ).scalar()
        
        total_raised = db.query(func.sum(Fund.current_amount)).scalar() or 0.0
        
        # Ticket stats
        tickets_sold = db.query(func.count(Ticket.id)).scalar()
        tickets_used = db.query(func.count(Ticket.id)).filter(
            Ticket.is_used == True
        ).scalar()
        
        # Queue stats (if Redis enabled)
        queue_stats = transaction_queue.get_queue_stats()
        
        return {
            "timestamp": now.isoformat(),
            "users": {
                "total": total_users,
                "new_today": new_users_today,
                "new_this_week": new_users_week
            },
            "transactions": {
                "total": total_txs,
                "confirmed": confirmed_txs,
                "failed": failed_txs,
                "pending": pending_txs,
                "success_rate": round(confirmed_txs / total_txs * 100, 2) if total_txs > 0 else 0
            },
            "volume": {
                "total_algo": round(total_volume, 2),
                "today_algo": round(today_volume, 2),
                "average_tx_algo": round(total_volume / confirmed_txs, 2) if confirmed_txs > 0 else 0
            },
            "fundraising": {
                "active_campaigns": active_funds,
                "total_raised_algo": round(total_raised, 2)
            },
            "tickets": {
                "sold": tickets_sold,
                "used": tickets_used,
                "unused": tickets_sold - tickets_used
            },
            "queue": queue_stats
        }
        
    except Exception as e:
        logger.error(f"Failed to generate dashboard stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users")
async def list_users(
    skip: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all users with pagination and search
    """
    try:
        query = db.query(User)
        
        if search:
            query = query.filter(
                (User.phone_number.like(f"%{search}%")) |
                (User.wallet_address.like(f"%{search}%"))
            )
        
        total = query.count()
        users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
        
        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "users": [
                {
                    "id": u.id,
                    "phone_number": u.phone_number,
                    "wallet_address": u.wallet_address,
                    "is_active": u.is_active,
                    "created_at": u.created_at.isoformat() if u.created_at else None
                }
                for u in users
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to list users: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{phone_number}")
async def get_user_details(
    phone_number: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get detailed user information including transaction history
    """
    try:
        user = db.query(User).filter(User.phone_number == phone_number).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get transaction stats
        sent_count = db.query(func.count(Transaction.id)).filter(
            Transaction.sender_phone == phone_number,
            Transaction.status == TransactionStatus.CONFIRMED
        ).scalar()
        
        received_count = db.query(func.count(Transaction.id)).filter(
            Transaction.receiver_phone == phone_number,
            Transaction.status == TransactionStatus.CONFIRMED
        ).scalar()
        
        sent_volume = db.query(func.sum(Transaction.amount)).filter(
            Transaction.sender_phone == phone_number,
            Transaction.status == TransactionStatus.CONFIRMED
        ).scalar() or 0.0
        
        received_volume = db.query(func.sum(Transaction.amount)).filter(
            Transaction.receiver_phone == phone_number,
            Transaction.status == TransactionStatus.CONFIRMED
        ).scalar() or 0.0
        
        # Recent transactions
        recent_txs = db.query(Transaction).filter(
            (Transaction.sender_phone == phone_number) |
            (Transaction.receiver_phone == phone_number)
        ).order_by(desc(Transaction.timestamp)).limit(10).all()
        
        return {
            "user": {
                "phone_number": user.phone_number,
                "wallet_address": user.wallet_address,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat() if user.created_at else None
            },
            "stats": {
                "transactions_sent": sent_count,
                "transactions_received": received_count,
                "volume_sent_algo": round(sent_volume, 2),
                "volume_received_algo": round(received_volume, 2)
            },
            "recent_transactions": [
                {
                    "id": tx.id,
                    "type": tx.transaction_type.value if tx.transaction_type else None,
                    "amount": tx.amount,
                    "status": tx.status.value if tx.status else None,
                    "timestamp": tx.timestamp.isoformat() if tx.timestamp else None
                }
                for tx in recent_txs
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get user details: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/funds")
async def list_funds(
    active_only: bool = False,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    List all fundraising campaigns
    """
    try:
        query = db.query(Fund)
        
        if active_only:
            query = query.filter(Fund.is_active == True)
        
        funds = query.order_by(desc(Fund.created_at)).all()
        
        return {
            "total": len(funds),
            "funds": [
                {
                    "id": f.id,
                    "title": f.title,
                    "description": f.description,
                    "goal_amount": f.goal_amount,
                    "current_amount": f.current_amount,
                    "is_goal_met": f.is_goal_met,
                    "is_active": f.is_active,
                    "contributors_count": f.contributors_count,
                    "creator_phone": f.creator_phone,
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in funds
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to list funds: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit-logs")
async def get_audit_logs(
    event_type: Optional[str] = None,
    user_phone: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get audit logs for security monitoring
    """
    try:
        query = db.query(AuditLog)
        
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        
        if user_phone:
            query = query.filter(AuditLog.user_phone == user_phone)
        
        logs = query.order_by(desc(AuditLog.timestamp)).limit(limit).all()
        
        return {
            "total": len(logs),
            "logs": [
                {
                    "id": log.id,
                    "event_type": log.event_type,
                    "action": log.action,
                    "user_phone": log.user_phone,
                    "success": log.success,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "details": log.details
                }
                for log in logs
            ]
        }
        
    except Exception as e:
        logger.error(f"Failed to get audit logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queue/clear")
async def clear_transaction_queue(
    queue_name: str = "all"
) -> Dict[str, str]:
    """
    Clear transaction queue (admin tool)
    """
    try:
        transaction_queue.clear_queue(queue_name)
        logger.info(f"Admin cleared queue: {queue_name}")
        
        return {
            "status": "success",
            "message": f"Queue '{queue_name}' cleared"
        }
        
    except Exception as e:
        logger.error(f"Failed to clear queue: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
