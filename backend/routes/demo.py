"""
Demo Dashboard API Routes
Live statistics for impressive judge demonstrations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from datetime import datetime

from backend.database import get_db
from backend.services.demo_metrics_service import get_demo_metrics
from backend.services.demo_freeze_service import DemoFreezeManager
from backend.services.pitch_metrics_service import get_pitch_metrics
from backend.utils.production_logging import ProductionLogger

logger = ProductionLogger.get_logger(__name__)

router = APIRouter(prefix="/demo", tags=["Demo"])


@router.get("/live-stats", response_model=Dict[str, Any])
async def get_live_demo_stats(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /demo/live-stats
    
    Real-time campus adoption statistics
    Perfect for live judge demonstrations
    
    Returns:
        {
            "active_users": 387,
            "today_transactions": 1240,
            "avg_settlement_time": "4.3 sec",
            "success_rate": "99.2%",
            "tickets_minted": 542,
            "funds_raised_algo": 2840.50,
            "weekly_volume_algo": 15234.75,
            "status": "live"
        }
    """
    try:
        metrics_service = get_demo_metrics(db)
        
        # Get all metrics
        wallet_metrics = metrics_service.get_active_wallet_metrics()
        tx_metrics = metrics_service.get_success_rate_metrics()
        volume_metrics = metrics_service.get_volume_metrics()
        settlement = metrics_service.get_average_settlement_time()
        fundraising = metrics_service.get_fundraising_metrics()
        tickets = metrics_service.get_ticket_metrics()
        
        # Format for dashboard display
        live_stats = {
            "active_users": wallet_metrics["weekly_active_users"],
            "today_transactions": tx_metrics["total_transactions"],
            "avg_settlement_time": f"{settlement['average_seconds']} sec",
            "success_rate": f"{tx_metrics['overall_success_rate']}%",
            "tickets_minted": tickets["total_tickets_minted"],
            "funds_raised_algo": fundraising["total_raised_algo"],
            "weekly_volume_algo": volume_metrics["week_volume_algo"],
            "status": "live"
        }
        
        logger.info("Live demo stats retrieved", extra={
            "active_users": live_stats["active_users"],
            "today_transactions": live_stats["today_transactions"]
        })
        
        return live_stats
        
    except Exception as e:
        logger.error(f"Failed to retrieve live demo stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve demo statistics")


@router.get("/comprehensive", response_model=Dict[str, Any])
async def get_comprehensive_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /demo/comprehensive
    
    All metrics in one call
    Perfect for full dashboard view
    Supports freeze mode for consistent presentations
    
    Returns comprehensive metrics including:
    - Wallet adoption
    - Transaction success rates
    - Volume statistics
    - Settlement times
    - Fundraising impact
    - NFT ticket sales
    - Daily trends
    - Transaction type breakdown
    """
    try:
        # Check if frozen
        if DemoFreezeManager.is_frozen():
            frozen = DemoFreezeManager.get_frozen_metrics()
            if frozen:
                logger.info("Serving frozen comprehensive metrics")
                return frozen
            else:
                logger.warning("DEMO_FREEZE enabled but no cache, serving live metrics")
        
        # Live metrics
        metrics_service = get_demo_metrics(db)
        comprehensive = metrics_service.get_comprehensive_demo_metrics()
        
        logger.info("Comprehensive metrics retrieved (live)")
        
        return comprehensive
        
    except Exception as e:
        logger.error(f"Failed to retrieve comprehensive metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve comprehensive metrics")


@router.get("/talking-points", response_model=List[str])
async def get_judge_talking_points(db: Session = Depends(get_db)) -> List[str]:
    """
    GET /demo/talking-points
    
    Generate impressive talking points for judges
    Perfect for pitch deck and live demos
    
    Returns:
        [
            "🎓 500 students onboarded with 77.4% activation rate",
            "⚡ 98.0% transaction success rate with 4.5s average settlement time",
            "💰 12345.67 ALGO total transaction volume across 2543 confirmed transactions"
        ]
    """
    try:
        metrics_service = get_demo_metrics(db)
        talking_points = metrics_service.get_judge_talking_points()
        
        logger.info(f"Generated {len(talking_points)} talking points")
        
        return talking_points
        
    except Exception as e:
        logger.error(f"Failed to generate talking points: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate talking points")


@router.get("/daily-trends", response_model=List[Dict[str, Any]])
async def get_daily_trends(
    days: int = 7,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """
    GET /demo/daily-trends?days=7
    
    Daily transaction trends for charts
    Perfect for visualizing growth
    
    Query Parameters:
        days: Number of days to retrieve (default: 7, max: 30)
    
    Returns:
        [
            {
                "date": "2026-05-01",
                "transactions": 145,
                "confirmed": 142,
                "volume_algo": 523.45,
                "success_rate": 97.9
            },
            ...
        ]
    """
    try:
        if days > 30:
            days = 30
        
        metrics_service = get_demo_metrics(db)
        daily_stats = metrics_service.get_daily_transaction_stats(days)
        
        logger.info(f"Retrieved {len(daily_stats)} days of trend data")
        
        return daily_stats
        
    except Exception as e:
        logger.error(f"Failed to retrieve daily trends: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve daily trends")


@router.get("/wallets", response_model=Dict[str, Any])
async def get_wallet_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /demo/wallets
    
    Wallet adoption and activity metrics
    
    Returns:
        {
            "total_wallets": 500,
            "active_wallets": 387,
            "activation_rate": 77.4,
            "new_today": 12,
            "new_this_week": 89,
            "weekly_active_users": 324
        }
    """
    try:
        metrics_service = get_demo_metrics(db)
        wallet_metrics = metrics_service.get_active_wallet_metrics()
        
        logger.info("Wallet metrics retrieved", extra={
            "total_wallets": wallet_metrics["total_wallets"],
            "active_wallets": wallet_metrics["active_wallets"]
        })
        
        return wallet_metrics
        
    except Exception as e:
        logger.error(f"Failed to retrieve wallet metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve wallet metrics")


@router.get("/transactions", response_model=Dict[str, Any])
async def get_transaction_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /demo/transactions
    
    Transaction success and reliability metrics
    
    Returns:
        {
            "overall_success_rate": 98.0,
            "last_24h_success_rate": 99.2,
            "total_transactions": 2543,
            "confirmed_transactions": 2492,
            "failed_transactions": 51
        }
    """
    try:
        metrics_service = get_demo_metrics(db)
        tx_metrics = metrics_service.get_success_rate_metrics()
        
        logger.info("Transaction metrics retrieved", extra={
            "success_rate": tx_metrics["overall_success_rate"],
            "total_transactions": tx_metrics["total_transactions"]
        })
        
        return tx_metrics
        
    except Exception as e:
        logger.error(f"Failed to retrieve transaction metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve transaction metrics")


@router.get("/volume", response_model=Dict[str, Any])
async def get_volume_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /demo/volume
    
    Transaction volume metrics
    
    Returns:
        {
            "total_volume_algo": 12345.67,
            "today_volume_algo": 523.45,
            "week_volume_algo": 3456.78,
            "average_transaction_algo": 4.86,
            "total_transactions": 2543
        }
    """
    try:
        metrics_service = get_demo_metrics(db)
        volume_metrics = metrics_service.get_volume_metrics()
        
        logger.info("Volume metrics retrieved", extra={
            "total_volume": volume_metrics["total_volume_algo"],
            "week_volume": volume_metrics["week_volume_algo"]
        })
        
        return volume_metrics
        
    except Exception as e:
        logger.error(f"Failed to retrieve volume metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve volume metrics")


@router.get("/fundraising", response_model=Dict[str, Any])
async def get_fundraising_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /demo/fundraising
    
    Fundraising campaign metrics
    
    Returns:
        {
            "total_campaigns": 5,
            "active_campaigns": 3,
            "successful_campaigns": 2,
            "success_rate": 40.0,
            "total_raised_algo": 2840.50,
            "total_goal_algo": 2500.00,
            "goal_progress": 113.6,
            "average_contributors": 45.2
        }
    """
    try:
        metrics_service = get_demo_metrics(db)
        fundraising_metrics = metrics_service.get_fundraising_metrics()
        
        logger.info("Fundraising metrics retrieved", extra={
            "total_campaigns": fundraising_metrics["total_campaigns"],
            "total_raised": fundraising_metrics["total_raised_algo"]
        })
        
        return fundraising_metrics
        
    except Exception as e:
        logger.error(f"Failed to retrieve fundraising metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve fundraising metrics")


@router.get("/tickets", response_model=Dict[str, Any])
async def get_ticket_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /demo/tickets
    
    NFT ticket metrics
    
    Returns:
        {
            "total_tickets_minted": 542,
            "valid_unused_tickets": 89,
            "used_tickets": 453,
            "unique_events": 2,
            "ticket_revenue_algo": 4235.50,
            "average_ticket_price": 7.81
        }
    """
    try:
        metrics_service = get_demo_metrics(db)
        ticket_metrics = metrics_service.get_ticket_metrics()
        
        logger.info("Ticket metrics retrieved", extra={
            "total_tickets": ticket_metrics["total_tickets_minted"],
            "unique_events": ticket_metrics["unique_events"]
        })
        
        return ticket_metrics
        
    except Exception as e:
        logger.error(f"Failed to retrieve ticket metrics: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve ticket metrics")


@router.get("/tx-types", response_model=Dict[str, Any])
async def get_transaction_type_breakdown(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /demo/tx-types
    
    Transaction type breakdown
    
    Returns:
        {
            "peer_payment": {"count": 2000, "volume_algo": 8234.50},
            "bill_split": {"count": 150, "volume_algo": 5342.25},
            "fundraising": {"count": 320, "volume_algo": 2840.50},
            "ticket_purchase": {"count": 601, "volume_algo": 4693.12}
        }
    """
    try:
        metrics_service = get_demo_metrics(db)
        type_breakdown = metrics_service.get_transaction_type_breakdown()
        
        logger.info("Transaction type breakdown retrieved")
        
        return type_breakdown
        
    except Exception as e:
        logger.error(f"Failed to retrieve transaction type breakdown: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve transaction type breakdown")


@router.get("/pitch-summary", response_model=Dict[str, Any])
async def get_pitch_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    GET /demo/pitch-summary
    
    Presentation Talking Points API
    Top 5 impact metrics + Top 3 insights + Closing statement
    
    Perfect for preparing pitch before judges
    
    Returns:
        {
            "top_metrics": [
                {"metric": "Activation Rate", "value": "77%", "statement": "..."},
                {"metric": "Daily Active Users", "value": "387", "statement": "..."},
                {"metric": "Transactions Per User", "value": "5.2", "statement": "..."},
                {"metric": "Campus Coverage", "value": "24%", "statement": "..."},
                {"metric": "Fraud Prevented", "value": "2.4 ALGO", "statement": "..."}
            ],
            "top_insights": [
                "Students actually USE this - 77% activation proves product-market fit",
                "Network effects working - 24% campus coverage drives viral growth",
                "High engagement - 5.2 transactions per user shows value"
            ],
            "closing_statement": "AlgoChat Pay solves real student pain points with proven traction...",
            "elevator_pitch": "500 students, 77% activation, 5.2 txs/user - real campus adoption!",
            "timestamp": "2025-01-15T10:30:00"
        }
    """
    try:
        pitch_service = get_pitch_metrics(db)
        
        # Get comprehensive metrics
        adoption = pitch_service.get_adoption_rate()
        daily_active = pitch_service.get_daily_active_wallets()
        txs_per_user = pitch_service.get_avg_transactions_per_user()
        campus_coverage = pitch_service.get_campus_coverage()
        trust_savings = pitch_service.get_trust_savings()
        
        # Get elevator pitch
        elevator = pitch_service.get_elevator_pitch_stats()
        
        # Get impact statements
        impact_statements = pitch_service.get_judge_impact_statements()
        
        # Build top 5 metrics for slides
        top_metrics = [
            {
                "metric": "Activation Rate",
                "value": f"{adoption['activation_rate_percent']:.1f}%",
                "statement": adoption['pitch_statement'],
                "details": {
                    "total_users": adoption['total_users'],
                    "transacted_users": adoption['transacted_users']
                }
            },
            {
                "metric": "Daily Active Users",
                "value": str(daily_active['today_active']),
                "statement": daily_active['pitch_statement'],
                "details": {
                    "yesterday": daily_active['yesterday_active'],
                    "growth": f"{daily_active['growth_percent']:.1f}%"
                }
            },
            {
                "metric": "Transactions Per User",
                "value": f"{txs_per_user['avg_transactions_per_user']:.1f}",
                "statement": txs_per_user['pitch_statement'],
                "details": {
                    "power_users": txs_per_user['power_users_5plus'],
                    "power_user_rate": f"{txs_per_user['power_user_rate_percent']:.1f}%"
                }
            },
            {
                "metric": "Campus Coverage",
                "value": f"{campus_coverage['coverage_percent']:.1f}%",
                "statement": campus_coverage['pitch_statement'],
                "details": {
                    "total_users": campus_coverage['total_users'],
                    "assumed_campus_size": campus_coverage['medium_campus']
                }
            },
            {
                "metric": "Fraud Prevented",
                "value": f"{trust_savings['fraud_prevented_algo']:.1f} ALGO",
                "statement": trust_savings['pitch_statement'],
                "details": {
                    "total_trust_savings": f"{trust_savings['total_trust_savings_algo']:.1f} ALGO",
                    "dispute_savings": f"${trust_savings['dispute_resolution_savings_usd']:.0f}"
                }
            }
        ]
        
        # Top 3 adoption insights
        top_insights = [
            impact_statements['adoption_proof'],
            impact_statements['daily_engagement'],
            impact_statements['high_transaction_rate']
        ]
        
        # Closing statement
        closing_statement = (
            f"AlgoChat Pay has proven product-market fit with {adoption['total_users']} students and "
            f"{adoption['activation_rate_percent']:.0f}% activation rate. We're not just another payment app - "
            f"we're the infrastructure layer for campus economies. With {campus_coverage['coverage_percent']:.0f}% "
            f"campus penetration and {daily_active['today_active']} daily active users, network effects are driving "
            f"organic growth. Our blockchain-secured platform has already prevented {trust_savings['fraud_prevented_algo']:.1f} ALGO "
            f"in fraud. The future of student payments is here, and it's running on Algorand."
        )
        
        response = {
            "top_metrics": top_metrics,
            "top_insights": top_insights,
            "closing_statement": closing_statement,
            "elevator_pitch": elevator['one_liner'],
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Pitch summary generated successfully")
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to generate pitch summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate pitch summary")
