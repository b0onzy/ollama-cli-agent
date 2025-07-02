"""Logging configuration for ollama-cli-agent."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str = "ollama-cli-agent",
    level: int = logging.INFO,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up a logger with console output.
    
    Args:
        name: Logger name
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers if logger already exists
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_string)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


# Create default logger
logger = setup_logger()