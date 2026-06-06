"""Router cho chức năng chơi với AI.

AI games tạo game_room thật trong DB để lưu lịch sử.
AI player dùng UUID cố định.
"""
import logging
import random
import uuid
from enum import Enum

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import UserResponse
from app.modules.games.models import GameRoom, GameRoomStatus, MoveHistory
from app.modules.games.repository import GameRepository
from app.modules.games.validation_client import get_initial_state, validate_move
from app.shared.schemas import ResponseEnvelope

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/games/ai", tags=["Games AI"])

# UUID cố định cho AI — không phải member thật
AI_PLAYER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

ANALYSIS_URLS = {
    "chess": settings.ANALYSIS_CHESS_URL,
    "xiangqi": settings.ANALYSIS_XIANGQI_URL,
    "go": settings.ANALYSIS_GO_URL,
    "gomoku": settings.ANALYSIS_GOMOKU_URL,
}

DIFFICULTY_DEPTH = {"easy": 3, "medium": 10, "hard": 18}


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class ColorChoice(str, Enum):
    white = "white"
    black = "black"
    random = "random"


# --- Schemas ---

class AIGameStartRequest(BaseModel):
    game_type: str
    difficulty: Difficulty = Difficulty.medium
    time_control: int = 600
    increment: int = 0
    player_color: ColorChoice = ColorChoice.white


class AIGameStartResponse(BaseModel):
    room_id: uuid.UUID
    player_color: str  # "white" or "black"
    fen: str
    ai_first_move: str | None = None  # nếu AI đi trước


class AIPlayRequest(BaseModel):
    room_id: uuid.UUID
    move: dict  # {"from": "e2", "to": "e4", "promotion": "q"}


class AIPlayResponse(BaseModel):
    valid: bool
    player_move_san: str = ""
    new_fen: str = ""
    ai_move: str | None = None
    ai_move_san: str | None = None
    ai_fen: str | None = None
    game_over: bool = False
    result: str | None = None
    turn: str = ""


# --- Endpoints ---

@router.post("/start", response_model=ResponseEnvelope[AIGameStartResponse])
async def start_ai_game(
    request: AIGameStartRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Tạo ván đấu với AI — tạo game_room trong DB."""
    # Xác định màu
    if request.player_color == ColorChoice.random:
        player_is_white = random.choice([True, False])
    else:
        player_is_white = request.player_color == ColorChoice.white

    white_id = current_user.member_id if player_is_white else AI_PLAYER_ID
    black_id = AI_PLAYER_ID if player_is_white else current_user.member_id

    # Tạo room
    room = GameRoom(
        white_player_id=white_id,
        black_player_id=black_id,
        game_type=request.game_type,
        time_control=request.time_control,
        increment=request.increment,
        status=GameRoomStatus.playing,
    )
    db.add(room)
    await db.commit()
    await db.refresh(room)

    # Lấy initial state
    state = await get_initial_state(request.game_type)
    fen = state.get("fen", "")
    room.fen = fen
    await db.commit()

    # Nếu AI đi trước (player cầm đen)
    ai_first_move = None
    if not player_is_white:
        ai_first_move = await _get_ai_move(fen, request.game_type, request.difficulty)
        if ai_first_move:
            result = await validate_move(request.game_type, fen, _parse_ai_move(request.game_type, ai_first_move))
            if result.valid:
                fen = result.new_fen
                repo = GameRepository(db)
                await repo.add_move(MoveHistory(room_id=room.id, move_number=1, notation=ai_first_move, fen_after=fen))
                room.fen = fen
                await db.commit()

    return ResponseEnvelope(data=AIGameStartResponse(
        room_id=room.id,
        player_color="white" if player_is_white else "black",
        fen=fen,
        ai_first_move=ai_first_move,
    ))


@router.post("/play", response_model=ResponseEnvelope[AIPlayResponse])
async def play_ai_move(
    request: AIPlayRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Player đi 1 nước → validate → AI trả lời."""
    repo = GameRepository(db)
    room = await repo.get_room_by_id(request.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Phòng không tồn tại")
    if room.status != GameRoomStatus.playing:
        raise HTTPException(status_code=400, detail="Ván đấu đã kết thúc")

    fen = room.fen or ""
    game_type = room.game_type

    # Validate player move
    result = await validate_move(game_type, fen, request.move)
    if not result.valid:
        return ResponseEnvelope(data=AIPlayResponse(valid=False))

    # Lưu player move
    moves = await repo.get_moves(request.room_id)
    move_num = len(moves) + 1
    uci = f"{request.move.get('from', '')}{request.move.get('to', '')}" if game_type not in ("gomoku", "go") else f"{request.move.get('row')},{request.move.get('col')}"
    await repo.add_move(MoveHistory(room_id=room.id, move_number=move_num, notation=uci, fen_after=result.new_fen))
    room.fen = result.new_fen
    await db.commit()

    # Check game over after player move
    if result.game_over:
        room.status = GameRoomStatus.finished
        room.result = result.result
        await db.commit()
        return ResponseEnvelope(data=AIPlayResponse(
            valid=True, player_move_san=uci, new_fen=result.new_fen,
            game_over=True, result=result.result, turn=result.turn,
        ))

    # AI responds
    difficulty = _get_room_difficulty(room)
    ai_uci = await _get_ai_move(result.new_fen, game_type, difficulty)
    ai_result = None
    ai_fen = result.new_fen

    if ai_uci:
        ai_move_dict = _parse_ai_move(game_type, ai_uci)
        ai_val = await validate_move(game_type, result.new_fen, ai_move_dict)
        if ai_val.valid:
            ai_fen = ai_val.new_fen
            await repo.add_move(MoveHistory(room_id=room.id, move_number=move_num + 1, notation=ai_uci, fen_after=ai_fen))
            room.fen = ai_fen
            if ai_val.game_over:
                room.status = GameRoomStatus.finished
                room.result = ai_val.result
            await db.commit()
            ai_result = ai_val

    resp = AIPlayResponse(
        valid=True, player_move_san=uci, new_fen=ai_fen,
        ai_move=ai_uci, ai_move_san=ai_uci, ai_fen=ai_fen,
        game_over=ai_result.game_over if ai_result else False,
        result=ai_result.result if ai_result else None,
        turn=ai_result.turn if ai_result else result.turn,
    )
    return ResponseEnvelope(data=resp)


@router.post("/resign", response_model=ResponseEnvelope[None])
async def resign_ai_game(
    room_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Player đầu hàng."""
    repo = GameRepository(db)
    room = await repo.get_room_by_id(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Phòng không tồn tại")
    room.status = GameRoomStatus.finished
    # AI thắng
    room.result = "black_win" if room.white_player_id != AI_PLAYER_ID else "white_win"
    await db.commit()
    return ResponseEnvelope(data=None, message="Đã đầu hàng")


# --- Helpers ---

async def _get_ai_move(fen: str, game_type: str, difficulty: Difficulty) -> str | None:
    base_url = ANALYSIS_URLS.get(game_type)
    if not base_url:
        return None
    depth = DIFFICULTY_DEPTH[difficulty.value]
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{base_url}/api/v1/analyze/suggest", json={"fen": fen, "depth": depth})
        if resp.status_code == 200:
            return resp.json().get("best_move")
    except Exception as exc:
        logger.error("AI move error: %s", exc)
    return None


def _parse_ai_move(game_type: str, move_str: str) -> dict:
    """Parse AI move string into the dict format expected by validate_move."""
    if game_type in ("gomoku", "go") and "," in move_str:
        parts = move_str.split(",")
        return {"row": int(parts[0]), "col": int(parts[1])}
    # Chess/xiangqi: UCI format "e2e4"
    return {"from": move_str[:2], "to": move_str[2:4]}


def _get_room_difficulty(room: GameRoom) -> Difficulty:
    """Infer difficulty from time_control (heuristic, có thể lưu riêng sau)."""
    if room.time_control <= 60:
        return Difficulty.easy
    elif room.time_control <= 300:
        return Difficulty.medium
    return Difficulty.hard
