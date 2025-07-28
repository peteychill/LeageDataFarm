"""
Logging utility for the League Data Farm project.
Provides consistent logging across all modules.
"""

import logging
import sys
from pathlib import Path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import LOG_LEVEL, LOG_FORMAT

def setup_logger(name: str, log_file: str = None) -> logging.Logger:
    """
    Set up a logger with consistent formatting and optional file output.
    
    Args:
        name: Logger name (usually __name__)
        log_file: Optional path to log file
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers if they already exist
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger 