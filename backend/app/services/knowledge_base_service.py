import uuid

from app.models.knowledge_base import KnowledgeBase
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseUpdate
from app.services.exceptions import NotFoundError


class KnowledgeBaseService:
    def __init__(self, repo: KnowledgeBaseRepository) -> None:
        self.repo = repo

    async def create(self, *, owner_id: uuid.UUID, payload: KnowledgeBaseCreate) -> KnowledgeBase:
        return await self.repo.create(
            owner_id=owner_id, name=payload.name, description=payload.description
        )

    async def list_for_owner(self, *, owner_id: uuid.UUID) -> list[KnowledgeBase]:
        return await self.repo.list_for_owner(owner_id)

    async def get(self, kb_id: uuid.UUID, *, owner_id: uuid.UUID) -> KnowledgeBase:
        kb = await self.repo.get_by_id(kb_id, owner_id=owner_id)
        if kb is None:
            raise NotFoundError("Knowledge base not found.")
        return kb

    async def update(
        self, kb_id: uuid.UUID, *, owner_id: uuid.UUID, payload: KnowledgeBaseUpdate
    ) -> KnowledgeBase:
        kb = await self.get(kb_id, owner_id=owner_id)
        fields = payload.model_dump(exclude_unset=True)
        return await self.repo.update(kb, fields=fields)

    async def delete(self, kb_id: uuid.UUID, *, owner_id: uuid.UUID) -> None:
        kb = await self.get(kb_id, owner_id=owner_id)
        await self.repo.delete(kb)
