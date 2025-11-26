from loguru import logger


def run_retention():
    logger.info({"event": "retention_job_executed"})
