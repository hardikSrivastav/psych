import sys
from pathlib import Path
from loguru import logger
from app.core.config import settings


def setup_logging():
    """Configure logging to write to /logs directory with rotation"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("/app/logs")
    log_dir.mkdir(exist_ok=True)
    
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level,
        colorize=True
    )
    
    # Add file loggers with rotation
    log_files = {
        "app.log": "General application logs",
        "chat.log": "Chat interactions and responses", 
        "rag.log": "RAG pipeline operations",
        "evaluation.log": "Model evaluation results",
        "error.log": "Error and exception tracking"
    }
    
    for filename, description in log_files.items():
        logger.add(
            log_dir / filename,
            format="[{time:YYYY-MM-DD HH:mm:ss}] [{level}] [{name}] {message}",
            level="INFO",
            rotation="1 day",
            retention="7 days",
            compression="zip",
            filter=lambda record: record["level"].name == "ERROR" if filename == "error.log" else True
        )
    
    logger.info("Logging configured successfully")
    return logger


# Initialize logging
setup_logging()
