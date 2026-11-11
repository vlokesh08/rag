import uuid

from app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    session_expiry,
    verify_password,
)
from app.models.user import User
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.services.exceptions import AuthError, ConflictError


class AuthService:
    def __init__(self, user_repo: UserRepository, session_repo: SessionRepository) -> None:
        self.user_repo = user_repo
        self.session_repo = session_repo

    async def sign_up(self, *, email: str, password: str) -> tuple[User, str]:
        existing = await self.user_repo.get_by_email(email)
        if existing is not None:
            raise ConflictError("An account with this email already exists.")

        user = await self.user_repo.create(email=email, hashed_password=hash_password(password))
        token = await self._create_session(user.id)
        return user, token

    async def sign_in(self, *, email: str, password: str) -> tuple[User, str]:
        user = await self.user_repo.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthError("Invalid email or password.")

        token = await self._create_session(user.id)
        return user, token

    async def sign_out(self, *, token: str) -> None:
        await self.session_repo.delete_by_token_hash(hash_session_token(token))

    async def get_user_for_token(self, token: str) -> User | None:
        session = await self.session_repo.get_valid_by_token_hash(hash_session_token(token))
        if session is None:
            return None
        return await self.user_repo.get_by_id(session.user_id)

    async def _create_session(self, user_id: uuid.UUID) -> str:
        token = generate_session_token()
        await self.session_repo.create(
            user_id=user_id,
            token_hash=hash_session_token(token),
            expires_at=session_expiry(),
        )
        return token
