import json
import uuid
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import CurrentUser, DbSession, get_llm_provider
from app.providers.llm.base import LLMProvider
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService
from app.services.exceptions import NotFoundError

router = APIRouter(prefix="/chat", tags=["chat"])


def get_chat_service(
    db: DbSession, llm_provider: Annotated[LLMProvider, Depends(get_llm_provider)]
) -> ChatService:
    return ChatService(ConversationRepository(db), MessageRepository(db), llm_provider)


def _format_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


async def _sse_body(
    service: ChatService, *, conversation_id: uuid.UUID, owner_id: uuid.UUID, content: str
) -> AsyncGenerator[str]:
    try:
        async for event, data in service.stream_chat_response(
            conversation_id=conversation_id, owner_id=owner_id, content=content
        ):
            yield _format_sse(event, data)
    except NotFoundError as exc:
        yield _format_sse("error", {"message": str(exc)})


@router.post("")
async def chat(
    payload: ChatRequest,
    current_user: CurrentUser,
    service: Annotated[ChatService, Depends(get_chat_service)],
) -> StreamingResponse:
    return StreamingResponse(
        _sse_body(
            service,
            conversation_id=payload.conversation_id,
            owner_id=current_user.id,
            content=payload.content,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
