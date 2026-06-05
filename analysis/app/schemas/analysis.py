from pydantic import BaseModel, Field


class PositionAnalysisRequest(BaseModel):
    game_type: str = Field(..., pattern="^(chess|xiangqi|go)$")
    fen: str  # FEN cho chess/xiangqi, move list cho go
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
    game_type: str = Field(..., pattern="^(chess|xiangqi|go)$")
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
    game_type: str = Field(..., pattern="^(chess|xiangqi|go)$")
    fen: str
    depth: int = Field(default=15, ge=1, le=25)


class SuggestMoveResponse(BaseModel):
    best_move: str
    evaluation: float
    eval_type: str


class EngineStatusResponse(BaseModel):
    chess: bool
    xiangqi: bool
    go: bool
