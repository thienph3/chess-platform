import uuid
from datetime import datetime

from pydantic import BaseModel


class NewsPostCreate(BaseModel):
    title: str
    content: str
    is_pinned: bool = False


class NewsPostResponse(BaseModel):
    id: uuid.UUID
    title: str
    content: str
    author_id: uuid.UUID
    is_pinned: bool
    created_at: datetime

    model_config = {"from_attributes": True}
