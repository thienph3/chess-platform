from fastapi import APIRouter, Depends, status

from app.core.exceptions import AppException
from app.modules.auth.dependencies import get_auth_service, get_current_user
from app.modules.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.modules.auth.service import AuthService
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=ResponseEnvelope[TokenResponse])
async def login(data: LoginRequest, service: AuthService = Depends(get_auth_service)):
    tokens = await service.login(data)
    return ResponseEnvelope(data=tokens, message="Đăng nhập thành công")


@router.post(
    "/register",
    response_model=ResponseEnvelope[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register(data: RegisterRequest, service: AuthService = Depends(get_auth_service)):
    user = await service.register(data)
    return ResponseEnvelope(data=user, message="Đăng ký thành công")


@router.post("/refresh", response_model=ResponseEnvelope[TokenResponse])
async def refresh(data: RefreshRequest, service: AuthService = Depends(get_auth_service)):
    tokens = await service.refresh_token(data.refresh_token)
    return ResponseEnvelope(data=tokens, message="Làm mới token thành công")


@router.get("/me", response_model=ResponseEnvelope[UserResponse])
async def me(current_user: UserResponse = Depends(get_current_user)):
    return ResponseEnvelope(data=current_user, message="Thông tin người dùng")


@router.get("/users", response_model=ResponseEnvelope[list[UserResponse]])
async def list_users(
    current_user: UserResponse = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    if current_user.role != "admin":
        raise AppException("Không có quyền truy cập", status_code=403)
    users = await service.list_users()
    return ResponseEnvelope(data=users)


@router.post("/forgot-password", response_model=ResponseEnvelope[None])
async def forgot_password(
    data: ForgotPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.forgot_password(data.email)
    return ResponseEnvelope(data=None, message="Link đặt lại mật khẩu đã được gửi")


@router.post("/reset-password", response_model=ResponseEnvelope[None])
async def reset_password(
    data: ResetPasswordRequest,
    service: AuthService = Depends(get_auth_service),
):
    await service.reset_password(data.token, data.new_password)
    return ResponseEnvelope(data=None, message="Đặt lại mật khẩu thành công")
