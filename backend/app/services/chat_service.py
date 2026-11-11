import logging
import time
import uuid
from collections.abc import AsyncGenerator

from app.core.config import settings
from app.models.message import Message, MessageRole, MessageStatus
from app.providers.llm.base import ChatMessage, LLMProvider
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.services.exceptions import NotFoundError

logger = logging.getLogger(__name__)

RECENT_MESSAGE_WINDOW = 20


def _to_chat_message(message: Message) -> ChatMessage:
    return ChatMessage(role=message.role.value, content=message.content)


class ChatService:
    def __init__(
        self,
        conversation_repo: ConversationRepository,
        message_repo: MessageRepository,
        llm_provider: LLMProvider,
    ) -> None:
        self.conversation_repo = conversation_repo
        self.message_repo = message_repo
        self.llm_provider = llm_provider

    async def stream_chat_response(
        self, *, conversation_id: uuid.UUID, owner_id: uuid.UUID, content: str
    ) -> AsyncGenerator[tuple[str, dict]]:
        conversation = await self.conversation_repo.get_by_id(conversation_id, owner_id=owner_id)
        if conversation is None:
            raise NotFoundError("Conversation not found.")

        await self.message_repo.create(
            conversation_id=conversation_id, role=MessageRole.user, content=content
        )

        history = await self.message_repo.list_recent_for_conversation(
            conversation_id, limit=RECENT_MESSAGE_WINDOW
        )
        provider_messages = [_to_chat_message(m) for m in history]

        assistant_message_id = uuid.uuid4()
        yield "message_start", {
            "message_id": str(assistant_message_id),
            "conversation_id": str(conversation_id),
        }

        buffer: list[str] = []
        input_tokens: int | None = None
        output_tokens: int | None = None
        started_at = time.monotonic()
        status = MessageStatus.error  # overwritten to `complete` only on a clean finish
        failed = False

        try:
            async for event in self.llm_provider.stream_chat(provider_messages):
                if event.type == "delta" and event.text:
                    buffer.append(event.text)
                    yield "content_delta", {"delta": event.text}
                elif event.type == "done":
                    input_tokens = event.input_tokens
                    output_tokens = event.output_tokens
            status = MessageStatus.complete
        except Exception:
            logger.exception("LLM generation failed for conversation %s", conversation_id)
            failed = True
        finally:
            # Runs on a clean finish, a provider error, AND a client disconnect
            # (GeneratorExit), so the assistant's partial/complete reply is
            # always persisted exactly once.
            latency_ms = int((time.monotonic() - started_at) * 1000)
            await self.message_repo.create(
                message_id=assistant_message_id,
                conversation_id=conversation_id,
                role=MessageRole.assistant,
                content="".join(buffer),
                status=status,
                model=settings.anthropic_model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
            )

        if failed:
            yield "error", {"message": "The assistant failed to generate a response."}
        else:
            yield "message_complete", {
                "message_id": str(assistant_message_id),
                "content": "".join(buffer),
                "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
            }
