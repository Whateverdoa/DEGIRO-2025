import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


def setup_logging(
    app_name: str = "degiro-trading-agent",
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up comprehensive logging framework with different levels and handlers.
    
    Args:
        app_name: Name of the application for logger naming
        log_level: Default logging level (DEBUG, INFO, WARNING, ERROR)
        log_dir: Directory to store log files
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler - INFO and above
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler - All logs with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / f"{app_name}.log",
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # Error file handler - Only ERROR and CRITICAL
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / f"{app_name}_errors.log",
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # Trading activity log - Custom handler for trading operations
    trading_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / f"{app_name}_trading.log",
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    trading_handler.setLevel(logging.INFO)
    trading_formatter = logging.Formatter(
        '%(asctime)s - TRADING - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    trading_handler.setFormatter(trading_formatter)
    trading_handler.addFilter(lambda record: 'TRADING' in record.getMessage())
    logger.addHandler(trading_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: Name of the module/component
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f"degiro-trading-agent.{name}")


# Custom log levels for trading operations
TRADING_INFO = 25  # Between INFO and WARNING
logging.addLevelName(TRADING_INFO, "TRADING")

def trading_log(logger: logging.Logger, message: str, *args, **kwargs):
    """Log trading-specific information."""
    if logger.isEnabledFor(TRADING_INFO):
        logger._log(TRADING_INFO, message, args, **kwargs)