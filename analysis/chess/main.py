"""Chess Analysis Service — Stockfish engine."""
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.schemas import (
    ExportPgnRequest,
    ExportPgnResponse,
    GameReviewRequest,
    GameReviewResponse,
    InitialStateResponse,
    MoveClassificationResponse,
    PositionAnalysisRequest,
    PositionAnalysisResponse,
    SuggestMoveRequest,
    SuggestMoveResponse,
    ValidateMoveRequest,
    ValidateMoveResponse,
    VariationResponse,
)

from engine import ChessEngine

app = FastAPI(title="VCC Chess Analysis", docs_url="/api/docs")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

engine = ChessEngine()


@app.post("/api/v1/analyze/position", response_model=PositionAnalysisResponse)
async def analyze_position(req: PositionAnalysisRequest):
    result = await engine.analyze_position(req.fen, req.depth, req.num_variations)
    return PositionAnalysisResponse(
        eval_type=result.eval_type, value=result.value, best_move=result.best_move,
        variations=[VariationResponse(moves=v.moves, evaluation=v.evaluation, depth=v.depth) for v in result.variations],
        depth_reached=result.depth_reached,
    )


@app.post("/api/v1/analyze/game", response_model=GameReviewResponse)
async def review_game(req: GameReviewRequest):
    classifications = await engine.review_game(req.moves, req.depth)
    white_moves = [c for i, c in enumerate(classifications) if i % 2 == 0]
    black_moves = [c for i, c in enumerate(classifications) if i % 2 == 1]

    return GameReviewResponse(
        accuracy_white=calc_accuracy(white_moves, is_white=True),
        accuracy_black=calc_accuracy(black_moves, is_white=False),
        moves=[MoveClassificationResponse(
            move=c.move, eval_before=c.eval_before, eval_after=c.eval_after,
            best_move=c.best_move, classification=c.classification, depth=c.depth,
        ) for c in classifications],
        total_moves=len(classifications),
    )


import math


def _win_percent(cp: float) -> float:
    """Convert centipawns to win percentage (0-100), Lichess formula."""
    return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * cp)) - 1)


def calc_accuracy(moves, is_white: bool = True) -> float:
    """
    Accuracy per player (Lichess formula).
    Book moves are excluded from calculation.
    """
    if not moves:
        return 0.0

    non_book = [m for m in moves if m.classification != "book"]
    if not non_book:
        return 100.0  # all book moves

    total = 0.0
    for m in non_book:
        wp_before = _win_percent(m.eval_before)
        wp_after = _win_percent(m.eval_after)
        if is_white:
            delta = wp_before - wp_after
        else:
            delta = wp_after - wp_before
        raw = 103.1668 * math.exp(-0.04354 * max(0, delta)) - 3.1669
        total += max(0.0, min(100.0, raw))

    return round(total / len(non_book), 1)


@app.post("/api/v1/analyze/suggest", response_model=SuggestMoveResponse)
async def suggest_move(req: SuggestMoveRequest):
    result = await engine.analyze_position(req.fen, req.depth, 1)
    return SuggestMoveResponse(best_move=result.best_move, evaluation=result.value, eval_type=result.eval_type)


@app.get("/health")
async def health():
    available = await engine.is_available()
    return {"status": "ok" if available else "degraded", "engine": "stockfish"}


# --- Validation endpoints (dùng cho real-time gameplay) ---

import chess as chess_lib
import chess.pgn
import io


@app.get("/api/v1/initial-state", response_model=InitialStateResponse)
async def initial_state():
    return InitialStateResponse(fen=chess_lib.STARTING_FEN, turn="white", game_over=False)


@app.post("/api/v1/validate", response_model=ValidateMoveResponse)
async def validate_move(req: ValidateMoveRequest):
    try:
        board = chess_lib.Board(req.fen)
    except ValueError:
        return ValidateMoveResponse(valid=False)

    from_sq = req.move.get("from", "")
    to_sq = req.move.get("to", "")
    promotion = req.move.get("promotion", "")

    uci_str = f"{from_sq}{to_sq}{promotion}"
    try:
        move_obj = chess_lib.Move.from_uci(uci_str)
        if move_obj not in board.legal_moves:
            # Try without promotion
            move_obj = chess_lib.Move.from_uci(f"{from_sq}{to_sq}")
            if move_obj not in board.legal_moves:
                return ValidateMoveResponse(valid=False)
    except (ValueError, IndexError):
        return ValidateMoveResponse(valid=False)

    board.push(move_obj)

    result = None
    reason = None
    game_over = board.is_game_over()
    if game_over:
        if board.is_checkmate():
            result = "black_win" if board.turn else "white_win"
            reason = "checkmate"
        elif board.is_stalemate():
            result, reason = "draw", "stalemate"
        elif board.is_insufficient_material():
            result, reason = "draw", "insufficient_material"
        elif board.is_fifty_moves():
            result, reason = "draw", "fifty_moves"
        elif board.is_repetition():
            result, reason = "draw", "repetition"

    return ValidateMoveResponse(
        valid=True, new_fen=board.fen(),
        turn="white" if board.turn else "black",
        game_over=game_over, result=result, reason=reason,
    )


@app.post("/api/v1/export/pgn", response_model=ExportPgnResponse)
async def export_pgn(req: ExportPgnRequest):
    game = chess_lib.pgn.Game()
    for key, value in req.headers.items():
        game.headers[key] = value

    node = game
    board = game.board()
    for move_str in req.moves:
        try:
            move = board.parse_uci(move_str)
            node = node.add_variation(move)
            board.push(move)
        except (ValueError, chess_lib.InvalidMoveError):
            try:
                move = board.parse_san(move_str)
                node = node.add_variation(move)
                board.push(move)
            except (ValueError, chess_lib.InvalidMoveError):
                break

    exporter = chess_lib.pgn.StringExporter(headers=True, variations=False, comments=False)
    pgn_str = game.accept(exporter)
    return ExportPgnResponse(pgn=pgn_str)
