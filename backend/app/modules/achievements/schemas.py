"""Achievement schemas."""
import uuid
from datetime import datetime

from pydantic import BaseModel


class AchievementResponse(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    description: str
    icon: str
    condition_type: str
    condition_value: int

    model_config = {"from_attributes": True}


class MemberAchievementResponse(BaseModel):
    id: uuid.UUID
    member_id: uuid.UUID
    achievement_id: uuid.UUID
    earned_at: datetime
    achievement: AchievementResponse | None = None

    model_config = {"from_attributes": True}
