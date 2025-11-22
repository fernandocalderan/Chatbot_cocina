import os
from pathlib import Path

from loguru import logger

LOG_DIR = Path(__file__).resolve().parents[2] / "app" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger():
    logger.remove()
    log_path = LOG_DIR / "app.log"
    logger.add(
        log_path,
        rotation="10 MB",
        retention="7 days",
        serialize=True,
        format="{time} | {level} | {message}",
    )
    logger.add(
        sink=lambda msg: print(msg, end=""),
        format="{time} | {level} | {message}",
    )
    return logger
