import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared.base_model import BaseModel


class GameType(str, enum.Enum):
    chess = "chess"
    xiangqi = "xiangqi"
    go = "go"


class TimeFormat(str, enum.Enum):
    bullet = "bullet"
    blitz = "blitz"
    rapid = "rapid"
    standard = "standard"


class TournamentFormat(str, enum.Enum):
    round_robin = "round_robin"
    swiss = "swiss"
    knockout = "knockout"


class TournamentStatus(str, enum.Enum):
    draft = "draft"
    registration = "registration"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class ParticipantStatus(str, enum.Enum):
    registered = "registered"
    confirmed = "confirmed"
    withdrawn = "withdrawn"


class RoundStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TournamentMode(str, enum.Enum):
    online = "online"
    otb = "otb"


class MatchResult(str, enum.Enum):
    white_win = "white_win"
    black_win = "black_win"
    draw = "draw"
    pending = "pending"


class Tournament(BaseModel):
    __tablename__ = "tournaments"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    game_type: Mapped[GameType] = mapped_column(Enum(GameType))
    time_format: Mapped[TimeFormat] = mapped_column(Enum(TimeFormat))
    format: Mapped[TournamentFormat] = mapped_column(Enum(TournamentFormat))
    max_participants: Mapped[int] = mapped_column(Integer)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[TournamentStatus] = mapped_column(Enum(TournamentStatus), default=TournamentStatus.draft)
    mode: Mapped[TournamentMode] = mapped_column(Enum(TournamentMode), default=TournamentMode.online)
    spectator_delay: Mapped[int] = mapped_column(Integer, default=0)  # delay in seconds (0 = no delay)
    prizes_json: Mapped[list | None] = mapped_column(JSON, nullable=True, default=None)

    participants: Mapped[list["TournamentParticipant"]] = relationship(back_populates="tournament")
    rounds: Mapped[list["TournamentRound"]] = relationship(back_populates="tournament")


class TournamentParticipant(BaseModel):
    __tablename__ = "tournament_participants"

    tournament_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tournaments.id"))
    member_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id"))
    status: Mapped[ParticipantStatus] = mapped_column(Enum(ParticipantStatus), default=ParticipantStatus.registered)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    final_rank: Mapped[int | None] = mapped_column(Integer, nullable=True)

    tournament: Mapped["Tournament"] = relationship(back_populates="participants")


class TournamentRound(BaseModel):
    __tablename__ = "tournament_rounds"

    tournament_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tournaments.id"))
    round_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[RoundStatus] = mapped_column(Enum(RoundStatus), default=RoundStatus.pending)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    tournament: Mapped["Tournament"] = relationship(back_populates="rounds")
    matches: Mapped[list["Match"]] = relationship(back_populates="round")


class Match(BaseModel):
    __tablename__ = "matches"

    round_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tournament_rounds.id"))
    white_player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id"))
    black_player_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("members.id"))
    result: Mapped[MatchResult] = mapped_column(Enum(MatchResult), default=MatchResult.pending)
    played_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    round: Mapped["TournamentRound"] = relationship(back_populates="matches")
