"""Go Analysis Service — KataGo engine."""
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.schemas import (
    ExportPgnRequest,
    ExportPgnResponse,
    InitialStateResponse,
    PositionAnalysisRequest,
    PositionAnalysisResponse,
    SuggestMoveRequest,
    SuggestMoveResponse,
    ValidateMoveRequest,
    ValidateMoveResponse,
    VariationResponse,
)

from engine import GoEngine

app = FastAPI(title="VCC Go Analysis", docs_url="/api/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

engine = GoEngine()


@app.post("/api/v1/analyze/position", response_model=PositionAnalysisResponse)
async def analyze_position(req: PositionAnalysisRequest):
    result = await engine.analyze_position(req.fen, req.depth, req.num_variations)
    return PositionAnalysisResponse(
        eval_type=result.eval_type, value=result.value, best_move=result.best_move,
        variations=[VariationResponse(moves=v.moves, evaluation=v.evaluation, depth=v.depth) for v in result.variations],
        depth_reached=result.depth_reached,
    )


@app.post("/api/v1/analyze/suggest", response_model=SuggestMoveResponse)
async def suggest_move(req: SuggestMoveRequest):
    result = await engine.analyze_position(req.fen, req.depth, 1)
    return SuggestMoveResponse(best_move=result.best_move, evaluation=result.value, eval_type=result.eval_type)


@app.get("/health")
async def health():
    available = await engine.is_available()
    return {"status": "ok" if available else "degraded", "engine": "katago"}


# --- Validation endpoints ---
# Go validation dùng internal logic (ko rule, suicide) vì KataGo GTP không có validate command trực tiếp.

from engine import GoBoard as _GoBoard

_boards: dict[str, _GoBoard] = {}


def _get_or_create_board(fen: str) -> _GoBoard:
    """Parse FEN hoặc tạo board mới."""
    board = _GoBoard()
    if fen:
        board.load_fen(fen)
    return board


@app.get("/api/v1/initial-state", response_model=InitialStateResponse)
async def initial_state():
    board = _GoBoard()
    return InitialStateResponse(fen=board.to_fen(), turn="black", game_over=False)


@app.post("/api/v1/validate", response_model=ValidateMoveResponse)
async def validate_move(req: ValidateMoveRequest):
    board = _get_or_create_board(req.fen)
    action = req.move.get("action", "place")

    if action == "pass":
        board.pass_turn()
        game_over = board.is_game_over()
        result = None
        score = None
        if game_over:
            score = board.score()
            result = f"{score['winner']}_win"

        return ValidateMoveResponse(
            valid=True, new_fen=board.to_fen(),
            turn="black" if board.turn == 1 else "white",
            game_over=game_over, result=result, reason="double_pass" if game_over else None,
            score=score,
        )

    row = req.move.get("row")
    col = req.move.get("col")
    if row is None or col is None:
        return ValidateMoveResponse(valid=False)

    if not board.is_valid_move(row, col):
        return ValidateMoveResponse(valid=False)

    board.push(row, col)
    return ValidateMoveResponse(
        valid=True, new_fen=board.to_fen(),
        turn="black" if board.turn == 1 else "white",
        game_over=False,
        captures={"black": board.captures.get(1, 0), "white": board.captures.get(2, 0)},
    )


@app.post("/api/v1/export/pgn", response_model=ExportPgnResponse)
async def export_pgn(req: ExportPgnRequest):
    """Export Go game in SGF-like text format."""
    lines = [f'[{k} "{v}"]' for k, v in req.headers.items()]
    lines.append("")
    move_text = " ".join(f"{i + 1}.{m}" for i, m in enumerate(req.moves))
    lines.append(move_text)
    lines.append(req.headers.get("Result", "*"))
    return ExportPgnResponse(pgn="\n".join(lines))
