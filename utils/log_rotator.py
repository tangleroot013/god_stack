import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path("/home/tangleroot013/god_stack/logs")
LOG_FILE = LOG_DIR / "god_stack.log"
MAX_BYTES = 10 * 1024 * 1024  # 10 MiB limit per file
BACKUP_COUNT = 5

LOG_DIR.mkdir(parents=True, exist_ok=True)

def get_logger(name: str = "god_stack") -> logging.Logger:
    """Retrieves or configures a thread-safe rotating file stream logger."""
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    return logger
