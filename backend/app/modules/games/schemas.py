import uuid
from datetime import datetime

from pydantic import BaseModel

from app.modules.games.models import GameRoomStatus


class GameRoomCreate(BaseModel):
    game_type: str  # chess, xiangqi, go
    time_control: int = 300  # seconds
    increment: int = 0  # Fischer increment (seconds per move)
    black_player_id: uuid.UUID | None = None
    match_id: uuid.UUID | None = None


class ImportGameRequest(BaseModel):
    game_type: str  # chess, xiangqi, go
    white_player_id: uuid.UUID
    black_player_id: uuid.UUID
    result: str  # white_win, black_win, draw
    played_at: datetime | None = None
    moves: list[str] = []  # optional PGN moves
    rated: bool = True  # có tính ELO không
    tournament_id: uuid.UUID | None = None  # liên kết giải (optional)
    increment: int = 0


class GameRoomResponse(BaseModel):
    id: uuid.UUID
    match_id: uuid.UUID | None
    white_player_id: uuid.UUID
    black_player_id: uuid.UUID | None
    status: GameRoomStatus
    game_type: str
    time_control: int
    increment: int
    scheduled_start: datetime | None
    fen: str | None
    result: str | None
    white_accuracy: float | None
    black_accuracy: float | None
    is_reviewed: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class MoveHistoryResponse(BaseModel):
    id: uuid.UUID
    room_id: uuid.UUID
    move_number: int
    notation: str
    fen_after: str | None
    classification: str | None
    eval_after: int | None
    best_move: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
