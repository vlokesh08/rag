import uuid

from sqlalchemy import select

from app.models.message import Message, MessageRole, MessageStatus
from app.repositories.base import BaseRepository


class MessageRepository(BaseRepository):
    async def create(
        self,
        *,
        conversation_id: uuid.UUID,
        role: MessageRole,
        content: str,
        status: MessageStatus = MessageStatus.complete,
        model: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        latency_ms: int | None = None,
        message_id: uuid.UUID | None = None,
    ) -> Message:
        message = Message(
            id=message_id or uuid.uuid4(),
            conversation_id=conversation_id,
            role=role,
            content=content,
            status=status,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )
        self.db.add(message)
        await self.db.flush()
        return message

    async def list_for_conversation(self, conversation_id: uuid.UUID) -> list[Message]:
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        return list(result.scalars().all())

    async def list_recent_for_conversation(
        self, conversation_id: uuid.UUID, *, limit: int
    ) -> list[Message]:
        """Most recent `limit` messages, returned oldest-first for prompt context."""
        result = await self.db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        return list(reversed(result.scalars().all()))
