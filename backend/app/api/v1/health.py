from typing import Annotated

from arq.connections import ArqRedis
from fastapi import APIRouter, Depends, HTTPException, status
from redis.asyncio import Redis
from sqlalchemy import text

from app.api.deps import get_arq_pool
from app.core.config import settings
from app.core.database import engine

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def liveness() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
async def readiness() -> dict[str, str]:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable."
        ) from exc

    redis_client: Redis = Redis.from_url(settings.redis_url)
    try:
        await redis_client.ping()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Redis unavailable."
        ) from exc
    finally:
        await redis_client.aclose()

    return {"status": "ok"}


@router.post("/worker-ping")
async def worker_ping(
    arq_pool: Annotated[ArqRedis, Depends(get_arq_pool)],
) -> dict[str, str]:
    """Demonstrates the ARQ enqueue -> worker execute -> result round-trip.

    Scaffolding for Phase 2's real ingestion jobs; not a product endpoint.
    """
    job = await arq_pool.enqueue_job("ping")
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Could not enqueue job."
        )
    return {"job_id": job.job_id}
