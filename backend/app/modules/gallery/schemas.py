import uuid
from datetime import datetime

from pydantic import BaseModel


class GalleryImageResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    description: str | None
    filename: str
    url: str
    tournament_id: uuid.UUID | None
    uploaded_by: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class GalleryImageUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    tournament_id: uuid.UUID | None = None
