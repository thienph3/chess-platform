import uuid
from datetime import datetime

from pydantic import BaseModel


class MemberCreate(BaseModel):
    full_name: str
    email: str | None = None
    phone: str | None = None
    skill_level: str | None = None
    notes: str | None = None


class MemberUpdate(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    skill_level: str | None = None
    notes: str | None = None


class MemberResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str | None
    phone: str | None
    skill_level: str | None
    notes: str | None
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
