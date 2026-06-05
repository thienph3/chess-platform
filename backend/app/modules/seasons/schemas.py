"""Season schemas."""
import uuid
from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel


class SeasonCreate(BaseModel):
    name: str
    start_date: Date
    end_date: Date
    game_type: str


class SeasonResponse(BaseModel):
    id: uuid.UUID
    name: str
    start_date: Date
    end_date: Date
    is_active: bool
    game_type: str
    created_at: datetime

    model_config = {"from_attributes": True}
