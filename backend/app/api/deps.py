from typing import Annotated

from arq.connections import ArqRedis
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.providers.llm.base import LLMProvider
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

DbSession = Annotated[AsyncSession, Depends(get_db)]


def get_auth_service(db: DbSession) -> AuthService:
    return AuthService(UserRepository(db), SessionRepository(db))


async def get_current_user(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    token = request.cookies.get(settings.session_cookie_name)
    user = await auth_service.get_user_for_token(token) if token else None
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_llm_provider(request: Request) -> LLMProvider:
    return request.app.state.llm_provider


def get_arq_pool(request: Request) -> ArqRedis:
    return request.app.state.arq_pool
