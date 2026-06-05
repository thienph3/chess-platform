"""Gomoku Analysis Service — Rapfi engine."""
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.schemas import (
    InitialStateResponse,
    SuggestMoveRequest,
    SuggestMoveResponse,
    ValidateMoveRequest,
    ValidateMoveResponse,
)

from engine import GomokuBoard, GomokuEngine

app = FastAPI(title="VCC Gomoku Analysis", docs_url="/api/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

engine = GomokuEngine()


@app.get("/health")
async def health():
    available = await engine.is_available()
    return {"status": "ok" if available else "degraded", "engine": "rapfi"}


@app.get("/api/v1/initial-state", response_model=InitialStateResponse)
async def initial_state():
    return InitialStateResponse(fen=";1", turn="black", game_over=False)


@app.post("/api/v1/validate", response_model=ValidateMoveResponse)
async def validate_move(req: ValidateMoveRequest):
    board = GomokuBoard()
    board.load_fen(req.fen)

    row = req.move.get("row")
    col = req.move.get("col")
    if row is None or col is None:
        return ValidateMoveResponse(valid=False)

    if not board.is_valid_move(row, col):
        return ValidateMoveResponse(valid=False)

    board.push(row, col)
    game_over = False
    result = None
    reason = None

    if board.check_win(row, col):
        game_over = True
        winner = 3 - board.turn  # player who just moved
        result = "white_win" if winner == 2 else "black_win"
        reason = "five_in_a_row"
    elif board.is_full():
        game_over = True
        result = "draw"
        reason = "board_full"

    return ValidateMoveResponse(
        valid=True,
        new_fen=board.to_fen(),
        turn="black" if board.turn == 1 else "white",
        game_over=game_over,
        result=result,
        reason=reason,
    )


@app.post("/api/v1/analyze/suggest", response_model=SuggestMoveResponse)
async def suggest_move(req: SuggestMoveRequest):
    result = await engine.analyze_position(req.fen, req.depth, 1)
    return SuggestMoveResponse(best_move=result.best_move, evaluation=result.value, eval_type=result.eval_type)
