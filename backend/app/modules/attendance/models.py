"""Attendance models."""
import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class EventType(str, enum.Enum):
    regular = "regular"
    tournament = "tournament"
    special = "special"


class Attendance(BaseModel):
    __tablename__ = "attendance"

    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id"))
    date: Mapped[date] = mapped_column(Date)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), default=EventType.regular)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
