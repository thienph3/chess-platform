import uuid

from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import UserResponse
from app.modules.notifications.dependencies import get_notification_service
from app.modules.notifications.schemas import NotificationResponse, UnreadCountResponse
from app.modules.notifications.service import NotificationService
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=ResponseEnvelope[list[NotificationResponse]])
async def get_notifications(
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Danh sách thông báo của user hiện tại."""
    notifications = await service.get_notifications(current_user.id, limit)
    return ResponseEnvelope(data=notifications)


@router.get("/unread-count", response_model=ResponseEnvelope[UnreadCountResponse])
async def get_unread_count(
    current_user: UserResponse = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Số thông báo chưa đọc."""
    count = await service.get_unread_count(current_user.id)
    return ResponseEnvelope(data=UnreadCountResponse(count=count))


@router.patch(
    "/{notification_id}/read",
    response_model=ResponseEnvelope[NotificationResponse],
)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Đánh dấu một thông báo đã đọc."""
    notification = await service.mark_read(notification_id)
    return ResponseEnvelope(data=notification, message="Đã đánh dấu đọc")


@router.patch("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    current_user: UserResponse = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
):
    """Đánh dấu tất cả thông báo đã đọc."""
    await service.mark_all_read(current_user.id)
