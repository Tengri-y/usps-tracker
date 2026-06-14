"""Logging utilities."""

import sys
from pathlib import Path
from loguru import logger
from config.settings import settings


def setup_logger(name: str = __name__):
    """Configure and return logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    # Remove default handler
    logger.remove()

    # Ensure logs directory exists
    log_dir = Path(settings.log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    # Add console handler
    logger.add(
        sys.stdout,
        format="<level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=settings.log_level,
    )

    # Add file handler
    logger.add(
        settings.log_file,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level,
        rotation="500 MB",
        retention=5,
    )

    return logger


# Global logger instance
logger_instance = setup_logger()
