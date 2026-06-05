from datetime import datetime, timedelta, timezone
import logging
import secrets

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AppException, ConflictException
from app.modules.auth.models import User
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.members.models import Member

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"


def _hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    pwd_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    """Verify password against bcrypt hash."""
    pwd_bytes = password.encode("utf-8")[:72]
    return bcrypt.checkpw(pwd_bytes, hashed.encode("utf-8"))


class AuthService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository

    async def register(self, data: RegisterRequest) -> UserResponse:
        existing = await self.repository.get_by_email(data.email)
        if existing:
            raise ConflictException("Email đã được sử dụng")

        # Tạo member profile
        member = Member(full_name=data.full_name, email=data.email)
        self.repository.db.add(member)
        await self.repository.db.flush()

        # Tạo user account
        user = User(
            email=data.email,
            hashed_password=_hash_password(data.password),
            member_id=member.id,
        )
        user = await self.repository.create_user(user)
        return UserResponse.model_validate(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.repository.get_by_email(data.email)
        if not user or not _verify_password(data.password, user.hashed_password):
            raise AppException("Email hoặc mật khẩu không đúng", status_code=401)
        if not user.is_active:
            raise AppException("Tài khoản đã bị vô hiệu hóa", status_code=403)
        return self._create_tokens(user)

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        payload = self._decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise AppException("Token không hợp lệ", status_code=401)
        user = await self.repository.get_by_id(payload["sub"])
        if not user or not user.is_active:
            raise AppException("Token không hợp lệ", status_code=401)
        return self._create_tokens(user)

    async def get_current_user(self, token: str) -> UserResponse:
        payload = self._decode_token(token)
        if payload.get("type") != "access":
            raise AppException("Token không hợp lệ", status_code=401)
        user = await self.repository.get_by_id(payload["sub"])
        if not user or not user.is_active:
            raise AppException("Token không hợp lệ", status_code=401)
        return UserResponse.model_validate(user)

    async def list_users(self) -> list[UserResponse]:
        users = await self.repository.list_all_users()
        return [UserResponse.model_validate(u) for u in users]

    def _create_tokens(self, user: User) -> TokenResponse:
        access_token = self._create_token(
            data={"sub": str(user.id), "type": "access"},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        refresh_token = self._create_token(
            data={"sub": str(user.id), "type": "refresh"},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    def _create_token(self, data: dict, expires_delta: timedelta) -> str:
        to_encode = data.copy()
        to_encode["exp"] = datetime.now(timezone.utc) + expires_delta
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    async def forgot_password(self, email: str) -> None:
        user = await self.repository.get_by_email(email)
        if not user:
            return  # Không tiết lộ email có tồn tại hay không
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        await self.repository.update_user(user)
        logger.info("PASSWORD RESET TOKEN [%s]: %s", email, token)

    async def reset_password(self, token: str, new_password: str) -> None:
        user = await self.repository.get_by_reset_token(token)
        if not user:
            raise AppException("Token không hợp lệ", status_code=400)
        if not user.reset_token_expires or user.reset_token_expires < datetime.now(timezone.utc):
            raise AppException("Token đã hết hạn", status_code=400)
        user.hashed_password = _hash_password(new_password)
        user.reset_token = None
        user.reset_token_expires = None
        await self.repository.update_user(user)

    def _decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        except JWTError:
            raise AppException("Token không hợp lệ hoặc đã hết hạn", status_code=401)
