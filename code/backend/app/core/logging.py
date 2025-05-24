import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from app.core.config import get_settings

settings = get_settings()

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        # Console handler
        logging.StreamHandler(sys.stdout),
        # File handler with rotation
        RotatingFileHandler(
            "logs/quantumnest.log", 
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
    ]
)

# Get logger
logger = logging.getLogger("quantumnest")

def get_logger(name: str) -> logging.Logger:
    """
    Get logger with specified name
    
    Parameters:
    -----------
    name : str
        Logger name
        
    Returns:
    --------
    logging.Logger
        Logger instance
    """
    return logging.getLogger(f"quantumnest.{name}")
