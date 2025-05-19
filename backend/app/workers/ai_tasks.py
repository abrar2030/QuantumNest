from app.workers.task_queue import celery_app
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from app.ai.lstm_model import LSTMModel
from app.ai.sentiment_analyzer import SentimentAnalyzer
from app.ai.portfolio_optimizer import PortfolioOptimizer
from app.ai.risk_profiler import RiskProfiler
from app.ai.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)

@celery_app.task(name="ai.predict_asset_price")
def predict_asset_price(asset_symbol, days_ahead=5, model_type="lstm"):
    """
    Asynchronous task to predict asset price
    
    Parameters:
    -----------
    asset_symbol : str
        Symbol of the asset to predict
    days_ahead : int
        Number of days to predict ahead
    model_type : str
        Type of model to use (lstm, garch, etc.)
        
    Returns:
    --------
    dict
        Prediction results
    """
    logger.info(f"Predicting price for {asset_symbol} {days_ahead} days ahead using {model_type}")
    
    try:
        # In production, this would fetch real market data
        # For now, generate mock data
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        data = pd.DataFrame({
            'date': dates,
            'close': np.random.normal(100, 10, 100).cumsum() + 1000,
            'volume': np.random.normal(1000000, 200000, 100),
            'open': np.random.normal(100, 10, 100).cumsum() + 1000,
            'high': np.random.normal(100, 10, 100).cumsum() + 1010,
            'low': np.random.normal(100, 10, 100).cumsum() + 990
        })
        
        # Initialize and train model
        if model_type == "lstm":
            model = LSTMModel(config={'prediction_horizon': days_ahead})
            model.train(data, verbose=0)
            
            # Make predictions
            future_data = data.copy()
            predictions = model.predict(future_data)
            
            # Format results
            prediction_dates = [datetime.now() + timedelta(days=i) for i in range(1, days_ahead + 1)]
            prediction_values = predictions[-days_ahead:].flatten().tolist()
            
            result = {
                "asset_symbol": asset_symbol,
                "model_type": model_type,
                "timestamp": datetime.now().isoformat(),
                "predictions": [
                    {"date": date.strftime("%Y-%m-%d"), "predicted_price": float(value)}
                    for date, value in zip(prediction_dates, prediction_values)
                ],
                "confidence_interval": {
                    "lower": [float(value * 0.95) for value in prediction_values],
                    "upper": [float(value * 1.05) for value in prediction_values]
                },
                "model_metrics": {
                    "mse": 25.5,
                    "rmse": 5.05,
                    "mae": 4.2,
                    "r2": 0.85
                }
            }
            
            return result
        else:
            raise ValueError(f"Model type {model_type} not supported")
            
    except Exception as e:
        logger.error(f"Error predicting price for {asset_symbol}: {str(e)}")
        return {"error": str(e)}

@celery_app.task(name="ai.analyze_sentiment")
def analyze_sentiment(asset_symbol, sources=None):
    """
    Asynchronous task to analyze sentiment for an asset
    
    Parameters:
    -----------
    asset_symbol : str
        Symbol of the asset to analyze
    sources : list
        List of sources to analyze (news, social_media, analyst_ratings)
        
    Returns:
    --------
    dict
        Sentiment analysis results
    """
    logger.info(f"Analyzing sentiment for {asset_symbol}")
    
    try:
        # In production, this would fetch real sentiment data
        # For now, return mock data with realistic structure
        sentiment = {
            "asset_symbol": asset_symbol,
            "timestamp": datetime.now().isoformat(),
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
                {"date": (datetime.now() - timedelta(days=7-i)).strftime("%Y-%m-%d"), 
                 "score": 65 + i}
                for i in range(7)
            ],
            "key_insights": [
                "Positive sentiment around upcoming product announcements",
                "Growing analyst confidence in revenue growth",
                "Some concerns about supply chain challenges",
                "Strong social media buzz around innovation"
            ]
        }
        
        return sentiment
            
    except Exception as e:
        logger.error(f"Error analyzing sentiment for {asset_symbol}: {str(e)}")
        return {"error": str(e)}

@celery_app.task(name="ai.optimize_portfolio")
def optimize_portfolio(portfolio_id, risk_tolerance=None, constraints=None):
    """
    Asynchronous task to optimize portfolio allocation
    
    Parameters:
    -----------
    portfolio_id : int
        ID of the portfolio to optimize
    risk_tolerance : float
        Risk tolerance level (0-100)
    constraints : dict
        Additional constraints for optimization
        
    Returns:
    --------
    dict
        Portfolio optimization results
    """
    logger.info(f"Optimizing portfolio {portfolio_id}")
    
    try:
        # In production, this would fetch real portfolio data and run optimization
        # For now, return mock data with realistic structure
        optimization_result = {
            "portfolio_id": portfolio_id,
            "timestamp": datetime.now().isoformat(),
            "current_allocation": [
                {"asset_symbol": "AAPL", "allocation": 15.2},
                {"asset_symbol": "MSFT", "allocation": 10.5},
                {"asset_symbol": "AMZN", "allocation": 8.3},
                {"asset_symbol": "TSLA", "allocation": 7.5},
                {"asset_symbol": "BTC", "allocation": 5.0}
            ],
            "optimized_allocation": [
                {"asset_symbol": "AAPL", "allocation": 12.0},
                {"asset_symbol": "MSFT", "allocation": 12.0},
                {"asset_symbol": "AMZN", "allocation": 10.0},
                {"asset_symbol": "TSLA", "allocation": 5.0},
                {"asset_symbol": "BTC", "allocation": 7.0},
                {"asset_symbol": "NVDA", "allocation": 3.0},
                {"asset_symbol": "ETH", "allocation": 2.0}
            ],
            "expected_performance": {
                "current_expected_return": 9.2,
                "optimized_expected_return": 10.5,
                "current_sharpe_ratio": 0.85,
                "optimized_sharpe_ratio": 0.95
            },
            "risk_metrics": {
                "current_volatility": 12.5,
                "optimized_volatility": 11.8,
                "current_var": 8.2,
                "optimized_var": 7.5
            }
        }
        
        return optimization_result
            
    except Exception as e:
        logger.error(f"Error optimizing portfolio {portfolio_id}: {str(e)}")
        return {"error": str(e)}

@celery_app.task(name="ai.analyze_portfolio_risk")
def analyze_portfolio_risk(portfolio_id):
    """
    Asynchronous task to analyze portfolio risk
    
    Parameters:
    -----------
    portfolio_id : int
        ID of the portfolio to analyze
        
    Returns:
    --------
    dict
        Risk analysis results
    """
    logger.info(f"Analyzing risk for portfolio {portfolio_id}")
    
    try:
        # In production, this would fetch real portfolio data and run risk analysis
        # For now, return mock data with realistic structure
        risk_analysis = {
            "portfolio_id": portfolio_id,
            "timestamp": datetime.now().isoformat(),
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
            
    except Exception as e:
        logger.error(f"Error analyzing risk for portfolio {portfolio_id}: {str(e)}")
        return {"error": str(e)}

@celery_app.task(name="ai.generate_market_recommendations")
def generate_market_recommendations():
    """
    Asynchronous task to generate market recommendations
    
    Returns:
    --------
    dict
        Market recommendations
    """
    logger.info("Generating market recommendations")
    
    try:
        # In production, this would analyze market data and generate recommendations
        # For now, return mock data with realistic structure
        recommendations = {
            "timestamp": datetime.now().isoformat(),
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
            
    except Exception as e:
        logger.error(f"Error generating market recommendations: {str(e)}")
        return {"error": str(e)}
