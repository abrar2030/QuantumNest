from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.main import get_current_active_user

router = APIRouter()

# Admin-only middleware
def admin_required(current_user: schemas.User = Depends(get_current_active_user)):
    if current_user.role != models.UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

@router.get("/dashboard", dependencies=[Depends(admin_required)])
def get_admin_dashboard(db: Session = Depends(get_db)):
    # This would be implemented with actual system data
    # For now, return mock data
    
    # Get user counts
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    
    # Get portfolio counts
    total_portfolios = db.query(models.Portfolio).count()
    
    # Get transaction counts
    total_transactions = db.query(models.Transaction).count()
    
    dashboard_data = {
        "timestamp": datetime.now(),
        "user_stats": {
            "total_users": total_users,
            "active_users": active_users,
            "user_growth": [
                {"month": "Jan", "users": 120},
                {"month": "Feb", "users": 150},
                {"month": "Mar", "users": 200},
                {"month": "Apr", "users": 250},
                {"month": "May", "users": 300},
                {"month": "Jun", "users": 380},
                {"month": "Jul", "users": 450},
            ],
            "user_tiers": {
                "basic": db.query(models.User).filter(models.User.tier == models.UserTier.BASIC).count(),
                "premium": db.query(models.User).filter(models.User.tier == models.UserTier.PREMIUM).count(),
                "enterprise": db.query(models.User).filter(models.User.tier == models.UserTier.ENTERPRISE).count()
            }
        },
        "portfolio_stats": {
            "total_portfolios": total_portfolios,
            "average_assets_per_portfolio": 8.5,
            "total_assets_under_management": 125000000
        },
        "transaction_stats": {
            "total_transactions": total_transactions,
            "transactions_today": 125,
            "transaction_volume_today": 2500000,
            "transaction_types": {
                "buy": 45,
                "sell": 35,
                "deposit": 15,
                "withdrawal": 5
            }
        },
        "system_health": {
            "api_uptime": 99.98,
            "database_performance": 95.5,
            "average_response_time": 120,  # ms
            "error_rate": 0.05,
            "active_sessions": 85
        },
        "alerts": [
            {
                "level": "warning",
                "message": "High API usage detected in the last hour",
                "timestamp": datetime.now() - timedelta(minutes=30)
            },
            {
                "level": "info",
                "message": "Database backup completed successfully",
                "timestamp": datetime.now() - timedelta(hours=2)
            },
            {
                "level": "critical",
                "message": "Multiple failed login attempts from IP 192.168.1.105",
                "timestamp": datetime.now() - timedelta(days=1)
            }
        ]
    }
    return dashboard_data

@router.get("/users", response_model=List[schemas.User], dependencies=[Depends(admin_required)])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users

@router.put("/users/{user_id}/activate", dependencies=[Depends(admin_required)])
def activate_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = True
    db.commit()
    db.refresh(db_user)
    return {"message": f"User {user_id} activated successfully"}

@router.put("/users/{user_id}/deactivate", dependencies=[Depends(admin_required)])
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    db_user.is_active = False
    db.commit()
    db.refresh(db_user)
    return {"message": f"User {user_id} deactivated successfully"}

@router.put("/users/{user_id}/change-tier", dependencies=[Depends(admin_required)])
def change_user_tier(user_id: int, tier_data: dict, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_tier = tier_data.get("tier")
    if new_tier not in [tier.value for tier in models.UserTier]:
        raise HTTPException(status_code=400, detail="Invalid tier value")
    
    db_user.tier = new_tier
    db.commit()
    db.refresh(db_user)
    return {"message": f"User {user_id} tier changed to {new_tier} successfully"}

@router.get("/transactions", dependencies=[Depends(admin_required)])
def get_all_transactions(skip: int = 0, limit: int = 100, status: Optional[str] = None, 
                        db: Session = Depends(get_db)):
    query = db.query(models.Transaction)
    if status:
        query = query.filter(models.Transaction.status == status)
    transactions = query.offset(skip).limit(limit).all()
    return transactions

@router.put("/transactions/{transaction_id}/update-status", dependencies=[Depends(admin_required)])
def update_transaction_status(transaction_id: int, status_data: dict, db: Session = Depends(get_db)):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    new_status = status_data.get("status")
    if new_status not in [status.value for status in models.TransactionStatus]:
        raise HTTPException(status_code=400, detail="Invalid status value")
    
    db_transaction.status = new_status
    db.commit()
    db.refresh(db_transaction)
    return {"message": f"Transaction {transaction_id} status updated to {new_status} successfully"}

@router.get("/system/logs", dependencies=[Depends(admin_required)])
def get_system_logs(skip: int = 0, limit: int = 100, log_level: Optional[str] = None, 
                   component: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(models.SystemLog)
    if log_level:
        query = query.filter(models.SystemLog.log_level == log_level)
    if component:
        query = query.filter(models.SystemLog.component == component)
    
    logs = query.order_by(models.SystemLog.timestamp.desc()).offset(skip).limit(limit).all()
    return logs

@router.post("/system/logs", dependencies=[Depends(admin_required)])
def create_system_log(log: schemas.SystemLogCreate, db: Session = Depends(get_db)):
    db_log = models.SystemLog(
        log_level=log.log_level,
        component=log.component,
        message=log.message
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/system/performance", dependencies=[Depends(admin_required)])
def get_system_performance():
    # This would be implemented with actual system monitoring
    # For now, return mock data
    performance_data = {
        "timestamp": datetime.now(),
        "cpu_usage": 35.2,  # percentage
        "memory_usage": 42.8,  # percentage
        "disk_usage": 68.5,  # percentage
        "network": {
            "incoming": 25.6,  # MB/s
            "outgoing": 18.2   # MB/s
        },
        "database": {
            "connections": 45,
            "query_time_avg": 28.5,  # ms
            "active_transactions": 12
        },
        "api": {
            "requests_per_minute": 250,
            "average_response_time": 120,  # ms
            "error_rate": 0.05  # percentage
        },
        "endpoints": [
            {"path": "/users", "requests": 45, "avg_time": 85},
            {"path": "/portfolio", "requests": 120, "avg_time": 150},
            {"path": "/market", "requests": 85, "avg_time": 110},
            {"path": "/ai", "requests": 35, "avg_time": 180},
            {"path": "/blockchain", "requests": 25, "avg_time": 200}
        ]
    }
    return performance_data

@router.post("/system/backup", dependencies=[Depends(admin_required)])
def trigger_system_backup():
    # This would be implemented with actual backup functionality
    # For now, return mock response
    return {
        "status": "success",
        "message": "System backup initiated",
        "backup_id": "bkp-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
        "timestamp": datetime.now(),
        "estimated_completion_time": datetime.now() + timedelta(minutes=15)
    }

@router.get("/analytics/user-activity", dependencies=[Depends(admin_required)])
def get_user_activity_analytics(days: int = 30):
    # This would be implemented with actual analytics data
    # For now, return mock data
    return {
        "period": f"Last {days} days",
        "total_active_users": 320,
        "average_session_duration": 18.5,  # minutes
        "average_sessions_per_user": 5.2,
        "most_active_times": [
            {"hour": 9, "activity": 85},
            {"hour": 12, "activity": 65},
            {"hour": 16, "activity": 92},
            {"hour": 20, "activity": 78}
        ],
        "most_used_features": [
            {"feature": "Portfolio View", "usage": 35},
            {"feature": "Market Analysis", "usage": 25},
            {"feature": "AI Recommendations", "usage": 20},
            {"feature": "Transactions", "usage": 15},
            {"feature": "Blockchain Explorer", "usage": 5}
        ],
        "user_retention": {
            "day1": 95,
            "day7": 85,
            "day30": 72
        }
    }

@router.post("/announcements", dependencies=[Depends(admin_required)])
def create_announcement(announcement_data: dict):
    # This would be implemented with actual announcement functionality
    # For now, return mock response
    return {
        "status": "success",
        "announcement_id": "ann-" + datetime.now().strftime("%Y%m%d-%H%M%S"),
        "title": announcement_data.get("title"),
        "message": announcement_data.get("message"),
        "target_users": announcement_data.get("target_users", "all"),
        "publish_time": datetime.now(),
        "expiry_time": datetime.now() + timedelta(days=int(announcement_data.get("expiry_days", 7)))
    }
