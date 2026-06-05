import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class GameRoomStatus(str, enum.Enum):
    waiting = "waiting"
    playing = "playing"
    finished = "finished"
    aborted = "aborted"


class ChallengeStatus(str, enum.Enum):
    pending = "pending"
    accepted = "accepted"
    declined = "declined"
    expired = "expired"


class GameRoom(BaseModel):
    __tablename__ = "game_rooms"

    match_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("matches.id"), nullable=True
    )
    white_player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id"))
    black_player_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("members.id"), nullable=True
    )
    status: Mapped[GameRoomStatus] = mapped_column(Enum(GameRoomStatus), default=GameRoomStatus.waiting)
    game_type: Mapped[str] = mapped_column(String(20))  # chess, xiangqi, go
    time_control: Mapped[int] = mapped_column(Integer, default=300)  # seconds per player
    increment: Mapped[int] = mapped_column(Integer, default=0)  # seconds added per move (Fischer)
    scheduled_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)  # khi nào bắt đầu (tournament)
    fen: Mapped[str | None] = mapped_column(Text, nullable=True)  # current position
    result: Mapped[str | None] = mapped_column(String(20), nullable=True)  # white_win, black_win, draw
    # Accuracy scores (chấm điểm bởi engine sau ván đấu)
    white_accuracy: Mapped[float | None] = mapped_column(nullable=True)
    black_accuracy: Mapped[float | None] = mapped_column(nullable=True)
    is_reviewed: Mapped[bool] = mapped_column(default=False)  # đã chấm điểm chưa


class MoveHistory(BaseModel):
    __tablename__ = "move_history"

    room_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("game_rooms.id"))
    move_number: Mapped[int] = mapped_column(Integer)
    notation: Mapped[str] = mapped_column(String(20))  # e.g. "e2e4", "Nf3"
    fen_after: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Review data (populated after game review)
    classification: Mapped[str | None] = mapped_column(String(20), nullable=True)  # brilliant, great, good, inaccuracy, mistake, blunder
    eval_after: Mapped[int | None] = mapped_column(Integer, nullable=True)  # centipawns
    best_move: Mapped[str | None] = mapped_column(String(20), nullable=True)


class Challenge(BaseModel):
    __tablename__ = "challenges"

    challenger_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id"))
    challenged_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id"))
    game_type: Mapped[str] = mapped_column(String(20))
    time_control: Mapped[int] = mapped_column(Integer, default=300)
    status: Mapped[ChallengeStatus] = mapped_column(Enum(ChallengeStatus), default=ChallengeStatus.pending)
