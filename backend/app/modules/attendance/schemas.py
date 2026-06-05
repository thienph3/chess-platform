"""Attendance schemas."""
import uuid
from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel


class AttendanceCreate(BaseModel):
    event_type: str = "regular"
    notes: str | None = None


class AttendanceResponse(BaseModel):
    id: uuid.UUID
    member_id: uuid.UUID
    date: Date
    event_type: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AttendanceSummary(BaseModel):
    total_sessions: int
    current_streak: int
    last_attendance: Date | None
