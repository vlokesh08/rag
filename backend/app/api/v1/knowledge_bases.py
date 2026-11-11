import uuid
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, DbSession
from app.repositories.knowledge_base_repository import KnowledgeBaseRepository
from app.schemas.knowledge_base import KnowledgeBaseCreate, KnowledgeBaseRead, KnowledgeBaseUpdate
from app.services.knowledge_base_service import KnowledgeBaseService

router = APIRouter(prefix="/knowledge-bases", tags=["knowledge-bases"])


def get_knowledge_base_service(db: DbSession) -> KnowledgeBaseService:
    return KnowledgeBaseService(KnowledgeBaseRepository(db))


ServiceDep = Annotated[KnowledgeBaseService, Depends(get_knowledge_base_service)]


@router.post("", response_model=KnowledgeBaseRead, status_code=201)
async def create_knowledge_base(
    payload: KnowledgeBaseCreate, current_user: CurrentUser, service: ServiceDep
) -> KnowledgeBaseRead:
    kb = await service.create(owner_id=current_user.id, payload=payload)
    return KnowledgeBaseRead.model_validate(kb)


@router.get("", response_model=list[KnowledgeBaseRead])
async def list_knowledge_bases(
    current_user: CurrentUser, service: ServiceDep
) -> list[KnowledgeBaseRead]:
    kbs = await service.list_for_owner(owner_id=current_user.id)
    return [KnowledgeBaseRead.model_validate(kb) for kb in kbs]


@router.get("/{kb_id}", response_model=KnowledgeBaseRead)
async def get_knowledge_base(
    kb_id: uuid.UUID, current_user: CurrentUser, service: ServiceDep
) -> KnowledgeBaseRead:
    kb = await service.get(kb_id, owner_id=current_user.id)
    return KnowledgeBaseRead.model_validate(kb)


@router.patch("/{kb_id}", response_model=KnowledgeBaseRead)
async def update_knowledge_base(
    kb_id: uuid.UUID,
    payload: KnowledgeBaseUpdate,
    current_user: CurrentUser,
    service: ServiceDep,
) -> KnowledgeBaseRead:
    kb = await service.update(kb_id, owner_id=current_user.id, payload=payload)
    return KnowledgeBaseRead.model_validate(kb)


@router.delete("/{kb_id}", status_code=204)
async def delete_knowledge_base(
    kb_id: uuid.UUID, current_user: CurrentUser, service: ServiceDep
) -> None:
    await service.delete(kb_id, owner_id=current_user.id)
