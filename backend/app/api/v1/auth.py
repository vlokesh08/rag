from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.api.deps import CurrentUser, get_auth_service
from app.core.config import settings
from app.schemas.auth import AuthResponse, SignInRequest, SignUpRequest
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_ttl_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


@router.post("/sign-up", response_model=AuthResponse, status_code=201)
async def sign_up(
    payload: SignUpRequest,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthResponse:
    user, token = await auth_service.sign_up(email=payload.email, password=payload.password)
    _set_session_cookie(response, token)
    return AuthResponse(user=UserRead.model_validate(user))


@router.post("/sign-in", response_model=AuthResponse)
async def sign_in(
    payload: SignInRequest,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthResponse:
    user, token = await auth_service.sign_in(email=payload.email, password=payload.password)
    _set_session_cookie(response, token)
    return AuthResponse(user=UserRead.model_validate(user))


@router.post("/sign-out", status_code=204)
async def sign_out(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> None:
    token = request.cookies.get(settings.session_cookie_name)
    if token:
        await auth_service.sign_out(token=token)
    response.delete_cookie(settings.session_cookie_name, path="/")


@router.get("/me", response_model=UserRead)
async def get_me(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
