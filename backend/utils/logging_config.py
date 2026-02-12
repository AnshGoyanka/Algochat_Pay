"""
Logging configuration for AlgoChat Pay
"""
import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger


def setup_logging(log_file: str = "logs/algochat.log", log_level: str = "INFO"):
    """
    Setup application logging
    
    Args:
        log_file: Path to log file
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    # Create logs directory
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler (human-readable)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    
    # File handler (JSON format)
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    json_format = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    file_handler.setFormatter(json_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get logger for specific module"""
    return logging.getLogger(name)
