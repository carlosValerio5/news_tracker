import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Configure logging format (CloudWatch-friendly with timestamps)
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# MAIN application logger
logger = logging.getLogger("news_tracker")