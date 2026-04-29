import logging
import signal
import sys
import atexit
from django.db import connections

logger = logging.getLogger(__name__)


def _handle_shutdown(signum, frame):
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    try:
        for conn in connections.all():
            conn.close()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    sys.exit(0)


def register_shutdown_handlers():
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)
    logger.info("Shutdown handlers registered")
