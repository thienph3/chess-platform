from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException
from app.db.session import get_db
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import UserResponse
from app.modules.auth.service import AuthService

security_scheme = HTTPBearer()


def get_auth_repository(db: AsyncSession = Depends(get_db)) -> AuthRepository:
    return AuthRepository(db)


def get_auth_service(repository: AuthRepository = Depends(get_auth_repository)) -> AuthService:
    return AuthService(repository)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    if not credentials:
        raise AppException("Chưa xác thực", status_code=401)
    return await service.get_current_user(credentials.credentials)


async def get_current_admin_user(
    current_user: UserResponse = Depends(get_current_user),
) -> UserResponse:
    if current_user.role != "admin":
        raise AppException("Không có quyền truy cập", status_code=403)
    return current_user
