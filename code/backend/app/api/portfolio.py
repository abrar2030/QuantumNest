from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.main import get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.Portfolio)
def create_portfolio(portfolio: schemas.PortfolioCreate, db: Session = Depends(get_db),
                    current_user: schemas.User = Depends(get_current_active_user)):
    db_portfolio = models.Portfolio(
        name=portfolio.name,
        description=portfolio.description,
        owner_id=current_user.id
    )
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

@router.get("/", response_model=List[schemas.Portfolio])
def read_portfolios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
                   current_user: schemas.User = Depends(get_current_active_user)):
    portfolios = db.query(models.Portfolio).filter(
        models.Portfolio.owner_id == current_user.id
    ).offset(skip).limit(limit).all()
    return portfolios

@router.get("/{portfolio_id}", response_model=schemas.PortfolioWithAssets)
def read_portfolio(portfolio_id: int, db: Session = Depends(get_db),
                  current_user: schemas.User = Depends(get_current_active_user)):
    db_portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.owner_id == current_user.id
    ).first()
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return db_portfolio

@router.put("/{portfolio_id}", response_model=schemas.Portfolio)
def update_portfolio(portfolio_id: int, portfolio: schemas.PortfolioCreate, db: Session = Depends(get_db),
                    current_user: schemas.User = Depends(get_current_active_user)):
    db_portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.owner_id == current_user.id
    ).first()
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    db_portfolio.name = portfolio.name
    db_portfolio.description = portfolio.description
    
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio

@router.delete("/{portfolio_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db),
                    current_user: schemas.User = Depends(get_current_active_user)):
    db_portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.owner_id == current_user.id
    ).first()
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    db.delete(db_portfolio)
    db.commit()
    return None

@router.post("/assets/", response_model=schemas.PortfolioAsset)
def add_asset_to_portfolio(portfolio_asset: schemas.PortfolioAssetCreate, db: Session = Depends(get_db),
                          current_user: schemas.User = Depends(get_current_active_user)):
    # Verify portfolio belongs to user
    db_portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_asset.portfolio_id,
        models.Portfolio.owner_id == current_user.id
    ).first()
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Verify asset exists
    db_asset = db.query(models.Asset).filter(models.Asset.id == portfolio_asset.asset_id).first()
    if db_asset is None:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    db_portfolio_asset = models.PortfolioAsset(
        portfolio_id=portfolio_asset.portfolio_id,
        asset_id=portfolio_asset.asset_id,
        quantity=portfolio_asset.quantity,
        purchase_price=portfolio_asset.purchase_price,
        purchase_date=portfolio_asset.purchase_date
    )
    db.add(db_portfolio_asset)
    db.commit()
    db.refresh(db_portfolio_asset)
    return db_portfolio_asset

@router.get("/assets/{portfolio_asset_id}", response_model=schemas.PortfolioAsset)
def read_portfolio_asset(portfolio_asset_id: int, db: Session = Depends(get_db),
                        current_user: schemas.User = Depends(get_current_active_user)):
    db_portfolio_asset = db.query(models.PortfolioAsset).join(
        models.Portfolio
    ).filter(
        models.PortfolioAsset.id == portfolio_asset_id,
        models.Portfolio.owner_id == current_user.id
    ).first()
    if db_portfolio_asset is None:
        raise HTTPException(status_code=404, detail="Portfolio asset not found")
    return db_portfolio_asset

@router.put("/assets/{portfolio_asset_id}", response_model=schemas.PortfolioAsset)
def update_portfolio_asset(portfolio_asset_id: int, portfolio_asset: schemas.PortfolioAssetCreate, 
                          db: Session = Depends(get_db),
                          current_user: schemas.User = Depends(get_current_active_user)):
    db_portfolio_asset = db.query(models.PortfolioAsset).join(
        models.Portfolio
    ).filter(
        models.PortfolioAsset.id == portfolio_asset_id,
        models.Portfolio.owner_id == current_user.id
    ).first()
    if db_portfolio_asset is None:
        raise HTTPException(status_code=404, detail="Portfolio asset not found")
    
    db_portfolio_asset.quantity = portfolio_asset.quantity
    db_portfolio_asset.purchase_price = portfolio_asset.purchase_price
    db_portfolio_asset.purchase_date = portfolio_asset.purchase_date
    
    db.commit()
    db.refresh(db_portfolio_asset)
    return db_portfolio_asset

@router.delete("/assets/{portfolio_asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_asset(portfolio_asset_id: int, db: Session = Depends(get_db),
                          current_user: schemas.User = Depends(get_current_active_user)):
    db_portfolio_asset = db.query(models.PortfolioAsset).join(
        models.Portfolio
    ).filter(
        models.PortfolioAsset.id == portfolio_asset_id,
        models.Portfolio.owner_id == current_user.id
    ).first()
    if db_portfolio_asset is None:
        raise HTTPException(status_code=404, detail="Portfolio asset not found")
    
    db.delete(db_portfolio_asset)
    db.commit()
    return None

@router.get("/performance/{portfolio_id}")
def get_portfolio_performance(portfolio_id: int, period: str = "1m", db: Session = Depends(get_db),
                             current_user: schemas.User = Depends(get_current_active_user)):
    # Verify portfolio belongs to user
    db_portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.owner_id == current_user.id
    ).first()
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # This would be implemented with actual calculations based on asset prices
    # For now, return mock data
    performance_data = {
        "portfolio_id": portfolio_id,
        "period": period,
        "start_value": 100000,
        "end_value": 110000,
        "return_percentage": 10.0,
        "benchmark_return": 8.5,
        "alpha": 1.5,
        "beta": 0.95,
        "sharpe_ratio": 1.2,
        "volatility": 12.5,
        "max_drawdown": -5.2,
        "data_points": [
            {"date": "2025-03-01", "value": 100000},
            {"date": "2025-03-15", "value": 105000},
            {"date": "2025-04-01", "value": 110000}
        ]
    }
    return performance_data
