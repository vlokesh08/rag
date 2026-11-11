import uuid

from app.models.conversation import Conversation
from app.models.message import Message
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.conversation import ConversationCreate
from app.services.exceptions import NotFoundError


class ConversationService:
    def __init__(
        self, conversation_repo: ConversationRepository, message_repo: MessageRepository
    ) -> None:
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo

    async def create(self, *, owner_id: uuid.UUID, payload: ConversationCreate) -> Conversation:
        return await self.conversation_repo.create(
            owner_id=owner_id, title=payload.title, knowledge_base_id=payload.knowledge_base_id
        )

    async def list_for_owner(self, *, owner_id: uuid.UUID) -> list[Conversation]:
        return await self.conversation_repo.list_for_owner(owner_id)

    async def get(self, conversation_id: uuid.UUID, *, owner_id: uuid.UUID) -> Conversation:
        conversation = await self.conversation_repo.get_by_id(conversation_id, owner_id=owner_id)
        if conversation is None:
            raise NotFoundError("Conversation not found.")
        return conversation

    async def delete(self, conversation_id: uuid.UUID, *, owner_id: uuid.UUID) -> None:
        conversation = await self.get(conversation_id, owner_id=owner_id)
        await self.conversation_repo.delete(conversation)

    async def list_messages(
        self, conversation_id: uuid.UUID, *, owner_id: uuid.UUID
    ) -> list[Message]:
        # Ownership check first so message listing can never leak another
        # user's conversation contents.
        await self.get(conversation_id, owner_id=owner_id)
        return await self.message_repo.list_for_conversation(conversation_id)
