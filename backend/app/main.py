from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from arq import create_pool
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.core.config import settings
from app.core.logging import configure_logging
from app.core.redis import get_arq_redis_settings
from app.providers.llm.anthropic_provider import AnthropicProvider
from app.services.exceptions import AuthError, ConflictError, DomainError, NotFoundError

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    app.state.llm_provider = AnthropicProvider()
    app.state.arq_pool = await create_pool(get_arq_redis_settings())
    yield
    await app.state.arq_pool.aclose()


app = FastAPI(title="RAG Knowledge Assistant API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_STATUS_BY_EXCEPTION = {
    NotFoundError: 404,
    ConflictError: 409,
    AuthError: 401,
}


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    status_code = next(
        (code for exc_type, code in _STATUS_BY_EXCEPTION.items() if isinstance(exc, exc_type)),
        400,
    )
    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


app.include_router(api_router)
