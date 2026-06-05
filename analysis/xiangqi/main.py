"""Xiangqi Analysis Service — Pikafish engine."""
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

from engine import XiangqiEngine

app = FastAPI(title="VCC Xiangqi Analysis", docs_url="/api/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

engine = XiangqiEngine()


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
    return {"status": "ok" if available else "degraded", "engine": "pikafish"}


# --- Validation endpoints ---

XIANGQI_STARTING_FEN = "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"


@app.get("/api/v1/initial-state", response_model=InitialStateResponse)
async def initial_state():
    return InitialStateResponse(fen=XIANGQI_STARTING_FEN, turn="red", game_over=False)


@app.post("/api/v1/validate", response_model=ValidateMoveResponse)
async def validate_move(req: ValidateMoveRequest):
    """Validate Xiangqi move bằng Pikafish engine (UCI 'position fen ... moves ...')."""
    from_row = req.move.get("from_row")
    from_col = req.move.get("from_col")
    to_row = req.move.get("to_row")
    to_col = req.move.get("to_col")

    if from_row is None or from_col is None or to_row is None or to_col is None:
        return ValidateMoveResponse(valid=False)

    # Convert row/col to UCI notation (Xiangqi: a0-i9)
    from_file = chr(ord("a") + from_col)
    from_rank = str(from_row)
    to_file = chr(ord("a") + to_col)
    to_rank = str(to_row)
    uci_move = f"{from_file}{from_rank}{to_file}{to_rank}"

    # Dùng Pikafish để validate: gửi position + move, nếu engine chấp nhận thì hợp lệ
    try:
        is_valid, new_fen, game_over_info = await engine.validate_move(req.fen, uci_move)
    except Exception:
        return ValidateMoveResponse(valid=False)

    if not is_valid:
        return ValidateMoveResponse(valid=False)

    # Determine turn from FEN
    parts = new_fen.split(" ")
    turn = "red" if len(parts) > 1 and parts[1] == "w" else "black"

    return ValidateMoveResponse(
        valid=True, new_fen=new_fen, turn=turn,
        game_over=game_over_info.get("game_over", False),
        result=game_over_info.get("result"),
        reason=game_over_info.get("reason"),
    )


@app.post("/api/v1/export/pgn", response_model=ExportPgnResponse)
async def export_pgn(req: ExportPgnRequest):
    """Export Xiangqi game in simple text format (no standard PGN for Xiangqi)."""
    lines = [f'[{k} "{v}"]' for k, v in req.headers.items()]
    lines.append("")
    # Number moves
    move_text = ""
    for i, move in enumerate(req.moves):
        if i % 2 == 0:
            move_text += f"{i // 2 + 1}. {move} "
        else:
            move_text += f"{move} "
    lines.append(move_text.strip())
    lines.append(req.headers.get("Result", "*"))
    return ExportPgnResponse(pgn="\n".join(lines))
