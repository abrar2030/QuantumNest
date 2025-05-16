"""
QuantumNest Capital Backend Application Package

This package contains the backend API and services for the QuantumNest Capital platform,
a comprehensive financial management and investment platform with AI-driven insights
and blockchain integration.

The application is built with FastAPI and provides RESTful API endpoints for:
- User authentication and management
- Portfolio management
- Market data analysis
- AI-powered recommendations
- Blockchain integration
- Administrative functions
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

# Create logs directory if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs"), exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs", "quantumnest.log"), 
            maxBytes=10485760, 
            backupCount=5
        ),
        logging.StreamHandler(sys.stdout)
    ]
)

# Import database models to ensure they are registered with SQLAlchemy
from app.models import models
from app.db.database import Base, engine

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Version information
__version__ = "0.1.0"
__author__ = "QuantumNest Capital Team"

# Package exports
__all__ = [
    "models",
    "schemas",
    "auth"
]

logger = logging.getLogger(__name__)
logger.info(f"QuantumNest Backend v{__version__} initialized")
