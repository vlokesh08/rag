import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DbSession
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.conversation import ConversationCreate, ConversationRead
from app.schemas.message import MessageRead
from app.services.conversation_service import ConversationService

router = APIRouter(prefix="/conversations", tags=["conversations"])


def get_conversation_service(db: DbSession) -> ConversationService:
    return ConversationService(ConversationRepository(db), MessageRepository(db))


ServiceDep = Annotated[ConversationService, Depends(get_conversation_service)]


@router.post("", response_model=ConversationRead, status_code=201)
async def create_conversation(
    payload: ConversationCreate, current_user: CurrentUser, service: ServiceDep
) -> ConversationRead:
    conversation = await service.create(owner_id=current_user.id, payload=payload)
    return ConversationRead.model_validate(conversation)


@router.get("", response_model=list[ConversationRead])
async def list_conversations(
    current_user: CurrentUser, service: ServiceDep
) -> list[ConversationRead]:
    conversations = await service.list_for_owner(owner_id=current_user.id)
    return [ConversationRead.model_validate(c) for c in conversations]


@router.get("/{conversation_id}", response_model=ConversationRead)
async def get_conversation(
    conversation_id: uuid.UUID, current_user: CurrentUser, service: ServiceDep
) -> ConversationRead:
    conversation = await service.get(conversation_id, owner_id=current_user.id)
    return ConversationRead.model_validate(conversation)


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: uuid.UUID, current_user: CurrentUser, service: ServiceDep
) -> None:
    await service.delete(conversation_id, owner_id=current_user.id)


@router.get("/{conversation_id}/messages", response_model=list[MessageRead])
async def list_messages(
    conversation_id: uuid.UUID, current_user: CurrentUser, service: ServiceDep
) -> list[MessageRead]:
    messages = await service.list_messages(conversation_id, owner_id=current_user.id)
    return [MessageRead.model_validate(m) for m in messages]
