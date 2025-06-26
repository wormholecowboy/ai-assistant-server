import logging
from logging.handlers import RotatingFileHandler
from .config import Config

def setup_logging():
    """Configure structured logging for the application."""
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                Config.LOG_FILE,
                maxBytes=5*1024*1024,  # 5MB
                backupCount=3
            ),
            logging.StreamHandler()
        ]
    )
    
    # Set log level for external libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('googleapiclient').setLevel(logging.INFO)
    logging.getLogger('supabase').setLevel(logging.INFO)
    
    return logging.getLogger(__name__)
