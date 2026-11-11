import uuid

from sqlalchemy import select

from app.models.conversation import Conversation
from app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository):
    async def create(
        self, *, owner_id: uuid.UUID, title: str | None, knowledge_base_id: uuid.UUID | None
    ) -> Conversation:
        conversation = Conversation(
            owner_id=owner_id, title=title, knowledge_base_id=knowledge_base_id
        )
        self.db.add(conversation)
        await self.db.flush()
        return conversation

    async def list_for_owner(self, owner_id: uuid.UUID) -> list[Conversation]:
        result = await self.db.execute(
            select(Conversation)
            .where(Conversation.owner_id == owner_id)
            .order_by(Conversation.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_by_id(
        self, conversation_id: uuid.UUID, *, owner_id: uuid.UUID
    ) -> Conversation | None:
        result = await self.db.execute(
            select(Conversation).where(
                Conversation.id == conversation_id, Conversation.owner_id == owner_id
            )
        )
        return result.scalar_one_or_none()

    async def delete(self, conversation: Conversation) -> None:
        await self.db.delete(conversation)
        await self.db.flush()
