import uuid
from datetime import datetime

from pydantic import BaseModel

from app.modules.notifications.models import NotificationType


class NotificationCreate(BaseModel):
    user_id: uuid.UUID
    title: str
    message: str
    type: NotificationType


class NotificationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: str
    type: NotificationType
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UnreadCountResponse(BaseModel):
    count: int
