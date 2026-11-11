from typing import Any


async def ping(ctx: dict[str, Any]) -> str:
    """Trivial job proving the ARQ/Redis/worker trigger pattern works end-to-end.

    Phase 2 replaces/extends this with real ingestion jobs (parse/chunk/embed).
    """
    return "pong"
