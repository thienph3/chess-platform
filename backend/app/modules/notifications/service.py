import uuid

from app.core.exceptions import NotFoundException
from app.modules.notifications.models import Notification
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import NotificationCreate, NotificationResponse


class NotificationService:
    def __init__(self, repository: NotificationRepository):
        self.repository = repository

    async def create_notification(self, data: NotificationCreate) -> NotificationResponse:
        notification = Notification(
            user_id=data.user_id,
            title=data.title,
            message=data.message,
            type=data.type,
        )
        notification = await self.repository.create(notification)
        return NotificationResponse.model_validate(notification)

    async def get_notifications(
        self, user_id: uuid.UUID, limit: int = 50
    ) -> list[NotificationResponse]:
        notifications = await self.repository.get_all(user_id, limit)
        return [NotificationResponse.model_validate(n) for n in notifications]

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        return await self.repository.get_unread_count(user_id)

    async def mark_read(self, notification_id: uuid.UUID) -> NotificationResponse:
        notification = await self.repository.mark_read(notification_id)
        if not notification:
            raise NotFoundException("Thông báo không tồn tại")
        return NotificationResponse.model_validate(notification)

    async def mark_all_read(self, user_id: uuid.UUID) -> None:
        await self.repository.mark_all_read(user_id)
