from app.core.logging import configure_logging
from app.core.redis import get_arq_redis_settings
from app.workers.jobs.health import ping

configure_logging()


class WorkerSettings:
    functions = [ping]
    redis_settings = get_arq_redis_settings()
