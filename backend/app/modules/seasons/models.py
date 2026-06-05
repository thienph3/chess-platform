"""Season/League models."""
import uuid
from datetime import date

from sqlalchemy import Boolean, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class Season(BaseModel):
    __tablename__ = "seasons"

    name: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    game_type: Mapped[str] = mapped_column(String(20))  # chess, xiangqi, go
