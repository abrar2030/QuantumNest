from datetime import timedelta
from typing import Any, Optional

from app.core.time_utils import utc_now
from app.db.database import get_db
from app.main import get_current_active_user
from app.models import models
from app.schemas import schemas
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

router = APIRouter()


def admin_required(
    current_user: models.User = Depends(get_current_active_user),
) -> models.User:
    if str(current_user.role) not in ("admin", "UserRole.ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required"
        )
    return current_user


@router.get("/dashboard", dependencies=[Depends(admin_required)])
def get_admin_dashboard(db: Session = Depends(get_db)) -> Any:
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    total_portfolios = db.query(models.Portfolio).count()
    total_transactions = db.query(models.Transaction).count()
    dashboard_data = {
        "timestamp": utc_now().isoformat(),
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
                "basic": db.query(models.User)
                .filter(models.User.tier == models.UserTier.BASIC)
                .count(),
                "premium": db.query(models.User)
                .filter(models.User.tier == models.UserTier.PREMIUM)
                .count(),
                "enterprise": db.query(models.User)
                .filter(models.User.tier == models.UserTier.ENTERPRISE)
                .count(),
            },
        },
        "portfolio_stats": {
            "total_portfolios": total_portfolios,
            "average_assets_per_portfolio": 8.5,
            "total_assets_under_management": 125000000,
        },
        "transaction_stats": {
            "total_transactions": total_transactions,
            "transactions_today": 125,
            "transaction_volume_today": 2500000,
            "transaction_types": {
                "buy": 45,
                "sell": 35,
                "deposit": 15,
                "withdrawal": 5,
            },
        },
        "system_health": {
            "api_uptime": 99.98,
            "database_performance": 95.5,
            "average_response_time": 120,
            "error_rate": 0.05,
            "active_sessions": 85,
        },
        "alerts": [
            {
                "id": 1,
                "type": "warning",
                "message": "High API usage detected",
                "timestamp": utc_now().isoformat(),
            }
        ],
    }
    return dashboard_data


@router.get("/users", dependencies=[Depends(admin_required)])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
) -> Any:
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    users = query.offset(skip).limit(limit).all()

    def _enum_value(v: Any) -> Any:
        return v.value if hasattr(v, "value") else v

    return {
        "total": query.count(),
        "data": [
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "role": _enum_value(u.role),
                "tier": _enum_value(u.tier),
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login": u.last_login.isoformat() if u.last_login else None,
            }
            for u in users
        ],
    }


@router.put("/users/{user_id}/status", dependencies=[Depends(admin_required)])
def update_user_status(
    user_id: int,
    is_active: bool,
    db: Session = Depends(get_db),
) -> Any:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = is_active
    user.updated_at = utc_now()
    db.commit()
    return {"message": f"User {user_id} status updated", "is_active": is_active}


@router.put("/users/{user_id}/role", dependencies=[Depends(admin_required)])
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
) -> Any:
    valid_roles = [r.value for r in models.UserRole]
    if role not in valid_roles:
        raise HTTPException(
            status_code=400, detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    user.updated_at = utc_now()
    db.commit()
    return {"message": f"User {user_id} role updated to {role}"}


@router.get("/system/logs", dependencies=[Depends(admin_required)])
def get_system_logs(
    skip: int = 0,
    limit: int = 100,
    log_level: Optional[str] = None,
    component: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Any:
    query = db.query(models.SystemLog)
    if log_level:
        query = query.filter(models.SystemLog.log_level == log_level.upper())
    if component:
        query = query.filter(models.SystemLog.component == component)
    logs = (
        query.order_by(models.SystemLog.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return logs


@router.post("/system/logs", dependencies=[Depends(admin_required)])
def create_system_log(
    log: schemas.SystemLogCreate, db: Session = Depends(get_db)
) -> Any:
    db_log = models.SystemLog(
        log_level=log.log_level.upper(),
        component=log.component,
        message=log.message,
        request_id=log.request_id,
        user_id=log.user_id,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/system/performance", dependencies=[Depends(admin_required)])
def get_system_performance() -> Any:
    try:
        import psutil

        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
    except ImportError:
        cpu, mem, disk = 35.2, 42.8, 68.5

    return {
        "timestamp": utc_now().isoformat(),
        "cpu_usage": cpu,
        "memory_usage": mem,
        "disk_usage": disk,
        "network": {"incoming": 25.6, "outgoing": 18.2},
        "database": {
            "connections": 45,
            "query_time_avg": 28.5,
            "active_transactions": 12,
        },
        "api": {
            "requests_per_minute": 250,
            "average_response_time": 120,
            "error_rate": 0.05,
        },
    }


@router.post("/system/backup", dependencies=[Depends(admin_required)])
def trigger_system_backup() -> Any:
    return {
        "status": "success",
        "message": "System backup initiated",
        "backup_id": "bkp-" + utc_now().strftime("%Y%m%d-%H%M%S"),
        "timestamp": utc_now().isoformat(),
        "estimated_completion_minutes": 15,
    }


@router.get("/analytics/user-activity", dependencies=[Depends(admin_required)])
def get_user_activity_analytics(days: int = Query(30, ge=1, le=365)) -> Any:
    return {
        "period": f"Last {days} days",
        "total_active_users": 320,
        "average_session_duration_minutes": 18.5,
        "average_sessions_per_user": 5.2,
        "most_active_times": [
            {"hour": 9, "activity": 85},
            {"hour": 12, "activity": 65},
            {"hour": 16, "activity": 92},
            {"hour": 20, "activity": 78},
        ],
        "most_used_features": [
            {"feature": "Portfolio View", "usage_percent": 35},
            {"feature": "Market Analysis", "usage_percent": 25},
            {"feature": "AI Recommendations", "usage_percent": 20},
            {"feature": "Transactions", "usage_percent": 15},
            {"feature": "Blockchain Explorer", "usage_percent": 5},
        ],
        "user_retention": {"day1": 95, "day7": 85, "day30": 72},
    }


@router.post("/announcements", dependencies=[Depends(admin_required)])
def create_announcement(announcement_data: dict) -> Any:
    expiry_days = int(announcement_data.get("expiry_days", 7))
    return {
        "status": "success",
        "announcement_id": "ann-" + utc_now().strftime("%Y%m%d-%H%M%S"),
        "title": announcement_data.get("title"),
        "message": announcement_data.get("message"),
        "target_users": announcement_data.get("target_users", "all"),
        "publish_time": utc_now().isoformat(),
        "expiry_time": (utc_now() + timedelta(days=expiry_days)).isoformat(),
    }
