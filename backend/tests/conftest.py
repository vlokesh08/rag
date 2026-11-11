from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.api.deps import get_arq_pool, get_llm_provider
from app.core.database import get_db
from app.main import app
from app.models.base import Base
from app.providers.llm.base import ChatMessage, LLMProvider, StreamEvent
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


class FakeLLMProvider(LLMProvider):
    """Deterministic in-memory provider so tests never need a real API key."""

    def __init__(self, reply: str = "This is a test reply.") -> None:
        self.reply = reply

    async def stream_chat(
        self, messages: list[ChatMessage], *, max_tokens: int | None = None
    ) -> AsyncGenerator[StreamEvent]:
        for word in self.reply.split(" "):
            yield StreamEvent(type="delta", text=word + " ")

    async def complete_chat(
        self, messages: list[ChatMessage], *, max_tokens: int | None = None
    ) -> str:
        return self.reply


@pytest_asyncio.fixture
async def test_engine():
    # StaticPool keeps a single connection alive for the engine's lifetime,
    # which is required for an in-memory SQLite DB to persist across queries.
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession]:
    session_factory = async_sessionmaker(bind=test_engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def fake_llm_provider() -> FakeLLMProvider:
    return FakeLLMProvider()


class FakeJob:
    job_id = "fake-job-id"


class FakeArqPool:
    """Avoids requiring a real Redis connection in unit/API tests."""

    async def enqueue_job(self, *_args: object, **_kwargs: object) -> FakeJob:
        return FakeJob()


@pytest_asyncio.fixture
async def client(db_session, fake_llm_provider) -> AsyncGenerator[AsyncClient]:
    async def _get_db_override() -> AsyncGenerator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_db] = _get_db_override
    app.dependency_overrides[get_llm_provider] = lambda: fake_llm_provider
    app.dependency_overrides[get_arq_pool] = lambda: FakeArqPool()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_service(db_session) -> AuthService:
    return AuthService(UserRepository(db_session), SessionRepository(db_session))


async def sign_up(client: AsyncClient, email: str, password: str = "supersecret1") -> dict:
    """Sign up on the given client; the client's cookie jar then carries the session."""
    response = await client.post(
        "/api/v1/auth/sign-up", json={"email": email, "password": password}
    )
    assert response.status_code == 201, response.text
    return response.json()["user"]
