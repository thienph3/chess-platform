import uuid

from sqlalchemy import Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.modules.tournaments.models import GameType, TimeFormat
from app.shared.base_model import BaseModel


class Rating(BaseModel):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("member_id", "game_type", "time_format", name="uq_rating_member_game_time"),
    )

    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id"))
    game_type: Mapped[GameType] = mapped_column(Enum(GameType))
    time_format: Mapped[TimeFormat] = mapped_column(Enum(TimeFormat))
    rating: Mapped[int] = mapped_column(Integer, default=1200)
    games_played: Mapped[int] = mapped_column(Integer, default=0)
    wins: Mapped[int] = mapped_column(Integer, default=0)
    draws: Mapped[int] = mapped_column(Integer, default=0)
    losses: Mapped[int] = mapped_column(Integer, default=0)

    changes: Mapped[list["RatingChange"]] = relationship(back_populates="rating_record")


class RatingChange(BaseModel):
    __tablename__ = "rating_changes"

    rating_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ratings.id"))
    match_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("matches.id"))
    old_rating: Mapped[int] = mapped_column(Integer)
    new_rating: Mapped[int] = mapped_column(Integer)
    change: Mapped[int] = mapped_column(Integer)

    rating_record: Mapped["Rating"] = relationship(back_populates="changes")
