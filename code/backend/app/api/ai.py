from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import models
from app.schemas import schemas
from app.main import get_current_active_user
from app.workers.ai_tasks import (
    predict_asset_price,
    analyze_sentiment,
    optimize_portfolio,
    analyze_portfolio_risk,
    generate_market_recommendations
)
from celery.result import AsyncResult
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Task status tracking
task_status_cache = {}

@router.get("/models/", response_model=List[schemas.AIModel])
async def get_ai_models(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """Get available AI models"""
    ai_models = db.query(models.AIModel).offset(skip).limit(limit).all()
    return ai_models

@router.get("/models/{model_id}", response_model=schemas.AIModel)
async def get_ai_model(
    model_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """Get specific AI model by ID"""
    db_model = db.query(models.AIModel).filter(models.AIModel.id == model_id).first()
    if db_model is None:
        raise HTTPException(status_code=404, detail="AI model not found")
    return db_model

@router.get("/predictions/", response_model=List[schemas.AIPrediction])
async def get_predictions(
    skip: int = 0, 
    limit: int = 100, 
    model_id: Optional[int] = None, 
    asset_id: Optional[int] = None, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """Get AI predictions with optional filtering"""
    query = db.query(models.AIPrediction)
    if model_id:
        query = query.filter(models.AIPrediction.model_id == model_id)
    if asset_id:
        query = query.filter(models.AIPrediction.asset_id == asset_id)
    predictions = query.offset(skip).limit(limit).all()
    return predictions

@router.get("/predictions/{prediction_id}", response_model=schemas.AIPrediction)
async def get_prediction(
    prediction_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """Get specific AI prediction by ID"""
    db_prediction = db.query(models.AIPrediction).filter(models.AIPrediction.id == prediction_id).first()
    if db_prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return db_prediction

@router.post("/predict/asset/{asset_symbol}")
async def predict_asset_future(
    asset_symbol: str,
    days_ahead: int = 5,
    model_type: str = "lstm",
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Predict future asset price asynchronously
    
    This endpoint triggers an asynchronous task and returns a task ID
    that can be used to check the status and retrieve results
    """
    try:
        # Submit task to Celery worker
        task = predict_asset_price.delay(asset_symbol, days_ahead, model_type)
        
        # Store task info
        task_info = {
            "task_id": task.id,
            "status": "PENDING",
            "user_id": current_user.id,
            "created_at": datetime.now().isoformat(),
            "task_type": "asset_price_prediction",
            "parameters": {
                "asset_symbol": asset_symbol,
                "days_ahead": days_ahead,
                "model_type": model_type
            }
        }
        
        # Store in cache (in production, use Redis or database)
        task_status_cache[task.id] = task_info
        
        # Return task ID for status checking
        return {
            "task_id": task.id,
            "status": "PENDING",
            "message": f"Prediction task for {asset_symbol} submitted successfully",
            "check_status_endpoint": f"/ai/tasks/{task.id}"
        }
        
    except Exception as e:
        logger.error(f"Error submitting prediction task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit prediction task: {str(e)}"
        )

@router.get("/tasks/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Check status of an asynchronous AI task
    
    Returns task status and result if available
    """
    try:
        # Get task result from Celery
        task_result = AsyncResult(task_id)
        
        # Get cached task info
        task_info = task_status_cache.get(task_id, {})
        
        # Check if task belongs to current user
        if task_info.get("user_id") and task_info.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to access this task"
            )
        
        # Prepare response
        response = {
            "task_id": task_id,
            "status": task_result.status,
            "task_type": task_info.get("task_type", "unknown"),
            "created_at": task_info.get("created_at"),
            "parameters": task_info.get("parameters", {})
        }
        
        # Include result if ready
        if task_result.ready():
            if task_result.successful():
                response["result"] = task_result.result
            else:
                response["error"] = str(task_result.result)
        
        return response
        
    except Exception as e:
        logger.error(f"Error checking task status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check task status: {str(e)}"
        )

@router.post("/sentiment/asset/{asset_symbol}")
async def analyze_asset_sentiment(
    asset_symbol: str,
    sources: Optional[List[str]] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Analyze sentiment for an asset asynchronously
    
    This endpoint triggers an asynchronous task and returns a task ID
    that can be used to check the status and retrieve results
    """
    try:
        # Submit task to Celery worker
        task = analyze_sentiment.delay(asset_symbol, sources)
        
        # Store task info
        task_info = {
            "task_id": task.id,
            "status": "PENDING",
            "user_id": current_user.id,
            "created_at": datetime.now().isoformat(),
            "task_type": "sentiment_analysis",
            "parameters": {
                "asset_symbol": asset_symbol,
                "sources": sources
            }
        }
        
        # Store in cache (in production, use Redis or database)
        task_status_cache[task.id] = task_info
        
        # Return task ID for status checking
        return {
            "task_id": task.id,
            "status": "PENDING",
            "message": f"Sentiment analysis task for {asset_symbol} submitted successfully",
            "check_status_endpoint": f"/ai/tasks/{task.id}"
        }
        
    except Exception as e:
        logger.error(f"Error submitting sentiment analysis task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit sentiment analysis task: {str(e)}"
        )

@router.post("/optimize/portfolio/{portfolio_id}")
async def optimize_user_portfolio(
    portfolio_id: int,
    risk_tolerance: Optional[float] = None,
    constraints: Optional[Dict[str, Any]] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Optimize portfolio allocation asynchronously
    
    This endpoint triggers an asynchronous task and returns a task ID
    that can be used to check the status and retrieve results
    """
    try:
        # Verify portfolio belongs to user
        db_portfolio = db.query(models.Portfolio).filter(
            models.Portfolio.id == portfolio_id,
            models.Portfolio.owner_id == current_user.id
        ).first()
        
        if db_portfolio is None:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Submit task to Celery worker
        task = optimize_portfolio.delay(portfolio_id, risk_tolerance, constraints)
        
        # Store task info
        task_info = {
            "task_id": task.id,
            "status": "PENDING",
            "user_id": current_user.id,
            "created_at": datetime.now().isoformat(),
            "task_type": "portfolio_optimization",
            "parameters": {
                "portfolio_id": portfolio_id,
                "risk_tolerance": risk_tolerance,
                "constraints": constraints
            }
        }
        
        # Store in cache (in production, use Redis or database)
        task_status_cache[task.id] = task_info
        
        # Return task ID for status checking
        return {
            "task_id": task.id,
            "status": "PENDING",
            "message": f"Portfolio optimization task for portfolio {portfolio_id} submitted successfully",
            "check_status_endpoint": f"/ai/tasks/{task.id}"
        }
        
    except Exception as e:
        logger.error(f"Error submitting portfolio optimization task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit portfolio optimization task: {str(e)}"
        )

@router.post("/risk/portfolio/{portfolio_id}")
async def analyze_portfolio_risk_async(
    portfolio_id: int,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Analyze portfolio risk asynchronously
    
    This endpoint triggers an asynchronous task and returns a task ID
    that can be used to check the status and retrieve results
    """
    try:
        # Verify portfolio belongs to user
        db_portfolio = db.query(models.Portfolio).filter(
            models.Portfolio.id == portfolio_id,
            models.Portfolio.owner_id == current_user.id
        ).first()
        
        if db_portfolio is None:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        # Submit task to Celery worker
        task = analyze_portfolio_risk.delay(portfolio_id)
        
        # Store task info
        task_info = {
            "task_id": task.id,
            "status": "PENDING",
            "user_id": current_user.id,
            "created_at": datetime.now().isoformat(),
            "task_type": "portfolio_risk_analysis",
            "parameters": {
                "portfolio_id": portfolio_id
            }
        }
        
        # Store in cache (in production, use Redis or database)
        task_status_cache[task.id] = task_info
        
        # Return task ID for status checking
        return {
            "task_id": task.id,
            "status": "PENDING",
            "message": f"Portfolio risk analysis task for portfolio {portfolio_id} submitted successfully",
            "check_status_endpoint": f"/ai/tasks/{task.id}"
        }
        
    except Exception as e:
        logger.error(f"Error submitting portfolio risk analysis task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit portfolio risk analysis task: {str(e)}"
        )

@router.post("/recommendations/market")
async def get_market_recommendations_async(
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    Generate market recommendations asynchronously
    
    This endpoint triggers an asynchronous task and returns a task ID
    that can be used to check the status and retrieve results
    """
    try:
        # Submit task to Celery worker
        task = generate_market_recommendations.delay()
        
        # Store task info
        task_info = {
            "task_id": task.id,
            "status": "PENDING",
            "user_id": current_user.id,
            "created_at": datetime.now().isoformat(),
            "task_type": "market_recommendations",
            "parameters": {}
        }
        
        # Store in cache (in production, use Redis or database)
        task_status_cache[task.id] = task_info
        
        # Return task ID for status checking
        return {
            "task_id": task.id,
            "status": "PENDING",
            "message": "Market recommendations task submitted successfully",
            "check_status_endpoint": f"/ai/tasks/{task.id}"
        }
        
    except Exception as e:
        logger.error(f"Error submitting market recommendations task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit market recommendations task: {str(e)}"
        )

# Legacy synchronous endpoints - kept for backward compatibility but marked as deprecated
@router.get("/recommendations/portfolio/{portfolio_id}", deprecated=True)
async def get_portfolio_recommendations_legacy(
    portfolio_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    DEPRECATED: Get portfolio recommendations synchronously
    Use the asynchronous endpoint /ai/optimize/portfolio/{portfolio_id} instead
    """
    # Verify portfolio belongs to user
    db_portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.owner_id == current_user.id
    ).first()
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # This would be implemented with actual AI recommendation logic
    # For now, return mock data
    recommendations = {
        "portfolio_id": portfolio_id,
        "timestamp": datetime.now(),
        "rebalance_recommendations": [
            {"asset_symbol": "AAPL", "current_allocation": 15.2, "recommended_allocation": 12.0, "action": "reduce"},
            {"asset_symbol": "MSFT", "current_allocation": 10.5, "recommended_allocation": 12.0, "action": "increase"},
            {"asset_symbol": "AMZN", "current_allocation": 8.3, "recommended_allocation": 10.0, "action": "increase"},
            {"asset_symbol": "TSLA", "current_allocation": 7.5, "recommended_allocation": 5.0, "action": "reduce"},
            {"asset_symbol": "BTC", "current_allocation": 5.0, "recommended_allocation": 7.0, "action": "increase"}
        ],
        "new_asset_recommendations": [
            {"asset_symbol": "NVDA", "recommended_allocation": 3.0, "reason": "Strong AI growth potential"},
            {"asset_symbol": "ETH", "recommended_allocation": 2.0, "reason": "Diversify crypto exposure"}
        ],
        "risk_assessment": {
            "current_risk_score": 72,
            "recommended_risk_score": 68,
            "volatility": "medium-high",
            "diversification_score": 65
        },
        "expected_performance": {
            "current_expected_return": 9.2,
            "recommended_expected_return": 10.5,
            "current_sharpe_ratio": 0.85,
            "recommended_sharpe_ratio": 0.95
        }
    }
    return recommendations

@router.get("/recommendations/market", deprecated=True)
async def get_market_recommendations_legacy(
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    DEPRECATED: Get market recommendations synchronously
    Use the asynchronous endpoint /ai/recommendations/market instead
    """
    # This would be implemented with actual AI market recommendation logic
    # For now, return mock data
    recommendations = {
        "timestamp": datetime.now(),
        "market_outlook": {
            "short_term": "bullish",
            "medium_term": "neutral",
            "long_term": "bullish",
            "confidence": 75
        },
        "sector_recommendations": [
            {"sector": "Technology", "outlook": "bullish", "confidence": 82},
            {"sector": "Healthcare", "outlook": "bullish", "confidence": 75},
            {"sector": "Finance", "outlook": "neutral", "confidence": 65},
            {"sector": "Energy", "outlook": "bearish", "confidence": 70},
            {"sector": "Consumer", "outlook": "neutral", "confidence": 60}
        ],
        "asset_recommendations": [
            {
                "asset_symbol": "AAPL",
                "recommendation": "buy",
                "target_price": 215.50,
                "confidence": 78,
                "time_horizon": "medium-term"
            },
            {
                "asset_symbol": "MSFT",
                "recommendation": "buy",
                "target_price": 420.00,
                "confidence": 82,
                "time_horizon": "long-term"
            },
            {
                "asset_symbol": "TSLA",
                "recommendation": "hold",
                "target_price": 180.00,
                "confidence": 65,
                "time_horizon": "short-term"
            },
            {
                "asset_symbol": "BTC",
                "recommendation": "buy",
                "target_price": 75000.00,
                "confidence": 72,
                "time_horizon": "medium-term"
            },
            {
                "asset_symbol": "XOM",
                "recommendation": "sell",
                "target_price": 95.00,
                "confidence": 68,
                "time_horizon": "short-term"
            }
        ],
        "economic_indicators_forecast": [
            {"indicator": "GDP Growth", "forecast": 3.0, "previous": 2.8, "confidence": 70},
            {"indicator": "Inflation Rate", "forecast": 2.3, "previous": 2.5, "confidence": 75},
            {"indicator": "Unemployment", "forecast": 3.7, "previous": 3.8, "confidence": 80},
            {"indicator": "Interest Rate", "forecast": 1.75, "previous": 2.0, "confidence": 85}
        ]
    }
    return recommendations

@router.get("/sentiment/asset/{asset_symbol}", deprecated=True)
async def get_asset_sentiment_legacy(
    asset_symbol: str, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    DEPRECATED: Get asset sentiment analysis synchronously
    Use the asynchronous endpoint /ai/sentiment/asset/{asset_symbol} instead
    """
    # This would be implemented with actual sentiment analysis
    # For now, return mock data
    sentiment = {
        "asset_symbol": asset_symbol,
        "timestamp": datetime.now(),
        "overall_sentiment": {
            "score": 72,  # 0-100, higher is more positive
            "label": "bullish",
            "confidence": 78
        },
        "sentiment_breakdown": {
            "news": {
                "score": 68,
                "sources_analyzed": 42,
                "key_topics": ["earnings", "product launch", "market share"]
            },
            "social_media": {
                "score": 75,
                "sources_analyzed": 1250,
                "key_topics": ["innovation", "leadership", "competition"]
            },
            "analyst_ratings": {
                "score": 70,
                "sources_analyzed": 15,
                "key_topics": ["valuation", "growth potential", "risks"]
            }
        },
        "sentiment_trend": [
            {"date": "2025-04-02", "score": 65},
            {"date": "2025-04-03", "score": 67},
            {"date": "2025-04-04", "score": 70},
            {"date": "2025-04-05", "score": 68},
            {"date": "2025-04-06", "score": 71},
            {"date": "2025-04-07", "score": 70},
            {"date": "2025-04-08", "score": 72}
        ],
        "key_insights": [
            "Positive sentiment around upcoming product announcements",
            "Growing analyst confidence in revenue growth",
            "Some concerns about supply chain challenges",
            "Strong social media buzz around innovation"
        ]
    }
    return sentiment

@router.get("/risk/portfolio/{portfolio_id}", deprecated=True)
async def get_portfolio_risk_analysis_legacy(
    portfolio_id: int, 
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    """
    DEPRECATED: Get portfolio risk analysis synchronously
    Use the asynchronous endpoint /ai/risk/portfolio/{portfolio_id} instead
    """
    # Verify portfolio belongs to user
    db_portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.owner_id == current_user.id
    ).first()
    if db_portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # This would be implemented with actual risk analysis
    # For now, return mock data
    risk_analysis = {
        "portfolio_id": portfolio_id,
        "timestamp": datetime.now(),
        "overall_risk_score": 65,  # 0-100, higher is riskier
        "risk_metrics": {
            "volatility": 12.5,
            "beta": 1.05,
            "value_at_risk": 8.2,
            "max_drawdown": 15.3,
            "sharpe_ratio": 0.85,
            "sortino_ratio": 1.2
        },
        "risk_breakdown": {
            "market_risk": 45,
            "sector_risk": 25,
            "asset_concentration_risk": 15,
            "currency_risk": 10,
            "liquidity_risk": 5
        },
        "stress_test_scenarios": [
            {"scenario": "Market Crash (-20%)", "portfolio_impact": -18.5},
            {"scenario": "Interest Rate Hike (+1%)", "portfolio_impact": -5.2},
            {"scenario": "Economic Recession", "portfolio_impact": -12.8},
            {"scenario": "Tech Sector Decline (-15%)", "portfolio_impact": -8.7},
            {"scenario": "Inflation Spike (+2%)", "portfolio_impact": -4.5}
        ],
        "risk_mitigation_recommendations": [
            "Reduce technology sector exposure by 5%",
            "Increase allocation to defensive assets",
            "Add hedging positions for key holdings",
            "Diversify cryptocurrency holdings"
        ]
    }
    return risk_analysis
