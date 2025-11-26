import rq
import redis

from loguru import logger

from app.core.config import get_settings


def start_worker():
    settings = get_settings()
    r = redis.from_url(settings.redis_url)
    q = rq.Queue("default", connection=r)
    worker = rq.Worker([q], connection=r)
    logger.info("Starting RQ worker")
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    start_worker()
