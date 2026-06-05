import uuid
from datetime import datetime

from pydantic import BaseModel

from app.modules.tournaments.models import GameType, TimeFormat


class RatingResponse(BaseModel):
    id: uuid.UUID
    member_id: uuid.UUID
    game_type: GameType
    time_format: TimeFormat
    rating: int
    games_played: int
    wins: int
    draws: int
    losses: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RatingChangeResponse(BaseModel):
    id: uuid.UUID
    rating_id: uuid.UUID
    match_id: uuid.UUID
    old_rating: int
    new_rating: int
    change: int
    created_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    id: uuid.UUID
    member_id: uuid.UUID
    rating: int
    games_played: int
    wins: int
    draws: int
    losses: int

    model_config = {"from_attributes": True}


class CalculateRequest(BaseModel):
    match_id: uuid.UUID
    rated: bool = True  # Có tính ELO hay không (mặc định có)


class CalculateResponse(BaseModel):
    white_player_id: uuid.UUID
    black_player_id: uuid.UUID
    white_old_rating: int
    white_new_rating: int
    black_old_rating: int
    black_new_rating: int
