import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select

from app.models.session import Session
from app.repositories.base import BaseRepository


class SessionRepository(BaseRepository):
    async def create(self, *, user_id: uuid.UUID, token_hash: str, expires_at: datetime) -> Session:
        session = Session(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.db.add(session)
        await self.db.flush()
        return session

    async def get_valid_by_token_hash(self, token_hash: str) -> Session | None:
        result = await self.db.execute(
            select(Session).where(
                Session.token_hash == token_hash,
                Session.expires_at > datetime.now(UTC),
            )
        )
        return result.scalar_one_or_none()

    async def delete_by_token_hash(self, token_hash: str) -> None:
        await self.db.execute(delete(Session).where(Session.token_hash == token_hash))
