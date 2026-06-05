"""Shared schemas cho tất cả analysis services."""
from pydantic import BaseModel, Field


class PositionAnalysisRequest(BaseModel):
    fen: str
    depth: int = Field(default=20, ge=1, le=30)
    num_variations: int = Field(default=3, ge=1, le=5)


class VariationResponse(BaseModel):
    moves: list[str]
    evaluation: float
    depth: int


class PositionAnalysisResponse(BaseModel):
    eval_type: str
    value: float
    best_move: str
    variations: list[VariationResponse]
    depth_reached: int


class GameReviewRequest(BaseModel):
    moves: list[str]
    depth: int = Field(default=18, ge=1, le=25)


class MoveClassificationResponse(BaseModel):
    move: str
    eval_before: float
    eval_after: float
    best_move: str
    classification: str
    depth: int


class GameReviewResponse(BaseModel):
    accuracy_white: float
    accuracy_black: float
    moves: list[MoveClassificationResponse]
    total_moves: int


class SuggestMoveRequest(BaseModel):
    fen: str
    depth: int = Field(default=15, ge=1, le=25)


class SuggestMoveResponse(BaseModel):
    best_move: str
    evaluation: float
    eval_type: str


# --- Validation schemas (dùng cho real-time gameplay) ---

class ValidateMoveRequest(BaseModel):
    fen: str
    move: dict  # Format tùy game type


class ValidateMoveResponse(BaseModel):
    valid: bool
    new_fen: str = ""
    turn: str = ""
    game_over: bool = False
    result: str | None = None
    reason: str | None = None
    captures: dict | None = None
    score: dict | None = None


class InitialStateResponse(BaseModel):
    fen: str
    turn: str
    game_over: bool = False


class ExportPgnRequest(BaseModel):
    moves: list[str]
    headers: dict[str, str] = {}


class ExportPgnResponse(BaseModel):
    pgn: str
