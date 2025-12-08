import structlog
from app.core.logging_config import configure_logging

# Configure logging on import
configure_logging()

def get_logger(name: str):
    """Get a structlog logger instance."""
    return structlog.get_logger(name)

# Get a default logger instance
logger = get_logger("app")
