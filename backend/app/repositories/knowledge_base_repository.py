import uuid

from sqlalchemy import select

from app.models.knowledge_base import KnowledgeBase
from app.repositories.base import BaseRepository


class KnowledgeBaseRepository(BaseRepository):
    async def create(
        self, *, owner_id: uuid.UUID, name: str, description: str | None
    ) -> KnowledgeBase:
        kb = KnowledgeBase(owner_id=owner_id, name=name, description=description)
        self.db.add(kb)
        await self.db.flush()
        return kb

    async def list_for_owner(self, owner_id: uuid.UUID) -> list[KnowledgeBase]:
        result = await self.db.execute(
            select(KnowledgeBase)
            .where(KnowledgeBase.owner_id == owner_id)
            .order_by(KnowledgeBase.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, kb_id: uuid.UUID, *, owner_id: uuid.UUID) -> KnowledgeBase | None:
        result = await self.db.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.id == kb_id, KnowledgeBase.owner_id == owner_id
            )
        )
        return result.scalar_one_or_none()

    async def update(self, kb: KnowledgeBase, *, fields: dict[str, object]) -> KnowledgeBase:
        for key, value in fields.items():
            setattr(kb, key, value)
        await self.db.flush()
        # `updated_at` is server-generated (onupdate=func.now()), so it's left
        # expired after the UPDATE; refresh now so later synchronous attribute
        # access (e.g. Pydantic's from_attributes) doesn't trigger a lazy load.
        await self.db.refresh(kb)
        return kb

    async def delete(self, kb: KnowledgeBase) -> None:
        await self.db.delete(kb)
        await self.db.flush()
