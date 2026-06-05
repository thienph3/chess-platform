import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification


class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, notification: Notification) -> Notification:
        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)
        return notification

    async def get_all(self, user_id: uuid.UUID, limit: int = 50) -> list[Notification]:
        query = (
            select(Notification)
            .where(Notification.user_id == user_id, Notification.is_deleted.is_(False))
            .order_by(Notification.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unread(self, user_id: uuid.UUID) -> list[Notification]:
        query = (
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
                Notification.is_deleted.is_(False),
            )
            .order_by(Notification.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_unread_count(self, user_id: uuid.UUID) -> int:
        query = (
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
                Notification.is_deleted.is_(False),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def mark_read(self, notification_id: uuid.UUID) -> Notification | None:
        query = select(Notification).where(
            Notification.id == notification_id, Notification.is_deleted.is_(False)
        )
        result = await self.db.execute(query)
        notification = result.scalar_one_or_none()
        if notification:
            notification.is_read = True
            await self.db.commit()
            await self.db.refresh(notification)
        return notification

    async def mark_all_read(self, user_id: uuid.UUID) -> None:
        stmt = (
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read.is_(False),
                Notification.is_deleted.is_(False),
            )
            .values(is_read=True)
        )
        await self.db.execute(stmt)
        await self.db.commit()
