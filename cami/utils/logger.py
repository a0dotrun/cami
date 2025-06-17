import logging
import sys


def setup_logger(
    name: str = "cami",
    level: str = "INFO",
    format_string: None | str = None,
) -> logging.Logger:
    """Setup and configure logger for the application.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages

    Returns:
        Configured logger instance
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Avoid adding handlers multiple times
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(getattr(logging, level.upper()))

        # Create formatter
        formatter = logging.Formatter(format_string)
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger


# Default logger instance that can be imported directly
logger = setup_logger()
