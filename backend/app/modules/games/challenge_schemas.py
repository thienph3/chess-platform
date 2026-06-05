"""Schemas cho hệ thống thách đấu."""
import uuid
from datetime import datetime

from pydantic import BaseModel


class ChallengeCreate(BaseModel):
    challenged_id: uuid.UUID
    game_type: str
    time_control: int = 300


class ChallengeResponse(BaseModel):
    id: uuid.UUID
    challenger_id: uuid.UUID
    challenged_id: uuid.UUID
    game_type: str
    time_control: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
