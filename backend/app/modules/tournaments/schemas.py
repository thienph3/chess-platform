import uuid
from datetime import date as Date
from datetime import datetime

from pydantic import BaseModel

from app.modules.tournaments.models import (
    GameType,
    MatchResult,
    ParticipantStatus,
    RoundStatus,
    TimeFormat,
    TournamentFormat,
    TournamentMode,
    TournamentStatus,
)


# --- Tournament schemas ---

class TournamentCreate(BaseModel):
    name: str
    description: str | None = None
    game_type: GameType
    time_format: TimeFormat
    format: TournamentFormat
    mode: TournamentMode = TournamentMode.online
    max_participants: int
    start_date: Date | None = None
    end_date: Date | None = None
    spectator_delay: int = 0


class TournamentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    game_type: GameType | None = None
    time_format: TimeFormat | None = None
    format: TournamentFormat | None = None
    mode: TournamentMode | None = None
    max_participants: int | None = None
    start_date: Date | None = None
    end_date: Date | None = None
    status: TournamentStatus | None = None
    spectator_delay: int | None = None


class TournamentResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    game_type: GameType
    time_format: TimeFormat
    format: TournamentFormat
    mode: TournamentMode
    max_participants: int
    start_date: Date | None
    end_date: Date | None
    status: TournamentStatus
    spectator_delay: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Participant schemas ---

class ParticipantCreate(BaseModel):
    member_id: uuid.UUID


class ParticipantResponse(BaseModel):
    id: uuid.UUID
    tournament_id: uuid.UUID
    member_id: uuid.UUID
    status: ParticipantStatus
    seed: int | None
    final_rank: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Round schemas ---

class RoundCreate(BaseModel):
    round_number: int
    start_time: datetime | None = None  # Chỉ dùng cho online tournaments


class MatchResponse(BaseModel):
    id: uuid.UUID
    round_id: uuid.UUID
    white_player_id: uuid.UUID
    black_player_id: uuid.UUID
    result: MatchResult
    played_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RoundResponse(BaseModel):
    id: uuid.UUID
    tournament_id: uuid.UUID
    round_number: int
    status: RoundStatus
    start_time: datetime | None
    matches: list[MatchResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Match schemas ---

class MatchResultUpdate(BaseModel):
    result: MatchResult
    played_at: datetime | None = None
    pgn: str | None = None  # Optional PGN cho OTB games


# --- Standings schemas ---

class StandingsEntry(BaseModel):
    rank: int
    member_id: uuid.UUID
    points: float
    wins: int
    draws: int
    losses: int
    buchholz: float
    sonneborn_berger: float


# --- Prize schemas ---

class TournamentPrize(BaseModel):
    rank: int
    prize_type: str  # cash, trophy, other
    prize_value: str  # "500,000 VNĐ", "Cúp vàng"
    member_id: uuid.UUID | None = None


class TournamentPrizeCreate(BaseModel):
    prizes: list[TournamentPrize]


class TournamentPrizeResponse(BaseModel):
    tournament_id: uuid.UUID
    prizes: list[TournamentPrize]
