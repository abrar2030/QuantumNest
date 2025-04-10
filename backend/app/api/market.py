from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.main import get_current_active_user

router = APIRouter()

@router.get("/assets/", response_model=List[schemas.Asset])
def get_assets(skip: int = 0, limit: int = 100, asset_type: Optional[str] = None, 
              db: Session = Depends(get_db),
              current_user: schemas.User = Depends(get_current_active_user)):
    query = db.query(models.Asset)
    if asset_type:
        query = query.filter(models.Asset.asset_type == asset_type)
    assets = query.offset(skip).limit(limit).all()
    return assets

@router.get("/assets/{asset_id}", response_model=schemas.Asset)
def get_asset(asset_id: int, db: Session = Depends(get_db),
             current_user: schemas.User = Depends(get_current_active_user)):
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    return db_asset

@router.get("/assets/{asset_id}/price")
def get_asset_price(asset_id: int, db: Session = Depends(get_db),
                   current_user: schemas.User = Depends(get_current_active_user)):
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Get latest price
    latest_price = db.query(models.AssetPrice).filter(
        models.AssetPrice.asset_id == asset_id
    ).order_by(models.AssetPrice.timestamp.desc()).first()
    
    if latest_price is None:
        raise HTTPException(status_code=404, detail="Price data not found")
    
    return {
        "asset_id": asset_id,
        "symbol": db_asset.symbol,
        "name": db_asset.name,
        "price": latest_price.price,
        "timestamp": latest_price.timestamp
    }

@router.get("/assets/{asset_id}/price_history")
def get_asset_price_history(asset_id: int, period: str = "1m", db: Session = Depends(get_db),
                           current_user: schemas.User = Depends(get_current_active_user)):
    db_asset = db.query(models.Asset).filter(models.Asset.id == asset_id).first()
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    # Calculate date range based on period
    end_date = datetime.now()
    if period == "1d":
        start_date = end_date - timedelta(days=1)
    elif period == "1w":
        start_date = end_date - timedelta(weeks=1)
    elif period == "1m":
        start_date = end_date - timedelta(days=30)
    elif period == "3m":
        start_date = end_date - timedelta(days=90)
    elif period == "6m":
        start_date = end_date - timedelta(days=180)
    elif period == "1y":
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)  # Default to 1 month
    
    # Get price history
    price_history = db.query(models.AssetPrice).filter(
        models.AssetPrice.asset_id == asset_id,
        models.AssetPrice.timestamp >= start_date,
        models.AssetPrice.timestamp <= end_date
    ).order_by(models.AssetPrice.timestamp.asc()).all()
    
    # Format response
    result = {
        "asset_id": asset_id,
        "symbol": db_asset.symbol,
        "name": db_asset.name,
        "period": period,
        "data": [{"timestamp": price.timestamp, "price": price.price} for price in price_history]
    }
    
    return result

@router.get("/market_summary")
def get_market_summary(db: Session = Depends(get_db),
                      current_user: schemas.User = Depends(get_current_active_user)):
    # This would be implemented with actual market data
    # For now, return mock data
    market_summary = {
        "indices": [
            {"name": "S&P 500", "value": 5350.24, "change": 30.12, "change_percent": 0.57},
            {"name": "NASDAQ", "value": 18200.75, "change": 50.45, "change_percent": 0.28},
            {"name": "Dow Jones", "value": 38900.18, "change": 45.32, "change_percent": 0.12}
        ],
        "sectors": [
            {"name": "Technology", "change_percent": 0.85},
            {"name": "Healthcare", "change_percent": 0.52},
            {"name": "Finance", "change_percent": 0.37},
            {"name": "Energy", "change_percent": -0.21},
            {"name": "Consumer", "change_percent": 0.43}
        ],
        "economic_indicators": [
            {"name": "GDP Growth", "value": 3.2, "previous": 2.8},
            {"name": "Inflation Rate", "value": 2.5, "previous": 2.7},
            {"name": "Unemployment", "value": 3.8, "previous": 4.0},
            {"name": "Interest Rate", "value": 2.0, "previous": 1.75}
        ],
        "market_sentiment": {
            "bullish": 61,
            "neutral": 23,
            "bearish": 16
        },
        "timestamp": datetime.now()
    }
    return market_summary

@router.get("/market_news")
def get_market_news(limit: int = 5, db: Session = Depends(get_db),
                   current_user: schemas.User = Depends(get_current_active_user)):
    # This would be implemented with actual news API
    # For now, return mock data
    market_news = [
        {
            "title": "Fed Signals Potential Rate Cut in Q3",
            "source": "Financial Times",
            "time": "2 hours ago",
            "summary": "Federal Reserve officials hinted at a possible interest rate cut in the third quarter as inflation pressures ease."
        },
        {
            "title": "Tech Stocks Rally on AI Breakthrough",
            "source": "Wall Street Journal",
            "time": "4 hours ago",
            "summary": "Major technology companies saw significant gains following announcements of new artificial intelligence capabilities."
        },
        {
            "title": "Global Supply Chain Improvements Boost Manufacturing",
            "source": "Bloomberg",
            "time": "6 hours ago",
            "summary": "Manufacturing indices show improvement as global supply chain disruptions continue to resolve."
        },
        {
            "title": "Energy Sector Faces Pressure Amid Renewable Push",
            "source": "Reuters",
            "time": "8 hours ago",
            "summary": "Traditional energy companies face challenges as governments worldwide accelerate renewable energy initiatives."
        },
        {
            "title": "Consumer Spending Remains Strong Despite Inflation",
            "source": "CNBC",
            "time": "10 hours ago",
            "summary": "Retail sales data indicates robust consumer spending despite ongoing inflation concerns."
        }
    ]
    return market_news[:limit]

@router.get("/sector_performance")
def get_sector_performance(period: str = "ytd", db: Session = Depends(get_db),
                          current_user: schemas.User = Depends(get_current_active_user)):
    # This would be implemented with actual sector performance data
    # For now, return mock data
    sector_performance = [
        {"name": "Technology", "value": 8.5},
        {"name": "Healthcare", "value": 5.2},
        {"name": "Finance", "value": 3.7},
        {"name": "Energy", "value": -2.1},
        {"name": "Consumer", "value": 4.3},
        {"name": "Utilities", "value": 1.8},
        {"name": "Materials", "value": 2.9},
        {"name": "Real Estate", "value": -1.5},
        {"name": "Industrials", "value": 3.2},
        {"name": "Telecom", "value": 2.5}
    ]
    return {"period": period, "data": sector_performance}
