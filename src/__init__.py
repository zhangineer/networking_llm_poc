from loguru import logger
import sys
from src.settings import get_settings

SETTINGS = get_settings()

LOG_LEVEL: str = SETTINGS.log_level.upper()
LOG_FORMAT: str = SETTINGS.log_format

# Initialize and configure the logger
logger.remove()  # Remove default logger

logger.add(
    sys.stderr,
    colorize=True,
    format=LOG_FORMAT,
    level="WARNING",
)

logger.add(
    "chat.log",
    colorize=False,
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    rotation="10 MB",
    filter=lambda record: record["extra"].get("log") == "chat",
    serialize=True
)