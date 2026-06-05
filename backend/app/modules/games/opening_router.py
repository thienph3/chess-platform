"""Opening Explorer — thống kê khai cuộc từ lịch sử ván đấu."""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.games.models import GameRoom, GameRoomStatus, MoveHistory
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/games/openings", tags=["Openings"])


class NextMoveStats(BaseModel):
    move: str
    count: int
    win_rate_white: float
    draw_rate: float
    win_rate_black: float


class OpeningStatsResponse(BaseModel):
    total_games: int
    white_wins: int
    black_wins: int
    draws: int
    next_moves: list[NextMoveStats]


@router.get("/stats", response_model=ResponseEnvelope[OpeningStatsResponse])
async def get_opening_stats(
    first_moves: str = Query("", description="Comma-separated moves, e.g. e2e4,e7e5"),
    game_type: str = Query("chess"),
    db: AsyncSession = Depends(get_db),
):
    """Thống kê khai cuộc dựa trên lịch sử ván đấu."""
    move_list = [m.strip() for m in first_moves.split(",") if m.strip()]
    depth = len(move_list)

    # Lấy tất cả game rooms đã kết thúc cho game_type
    rooms_query = (
        select(GameRoom.id, GameRoom.result)
        .where(
            GameRoom.game_type == game_type,
            GameRoom.status == GameRoomStatus.finished,
            GameRoom.is_deleted.is_(False),
        )
    )
    result = await db.execute(rooms_query)
    all_rooms = result.all()

    if not all_rooms:
        empty = OpeningStatsResponse(
            total_games=0, white_wins=0, black_wins=0, draws=0, next_moves=[]
        )
        return ResponseEnvelope(data=empty)

    room_ids = [r.id for r in all_rooms]
    room_results = {r.id: r.result for r in all_rooms}

    # Lọc rooms có đúng chuỗi nước đi đầu
    matching_room_ids = await _filter_rooms_by_moves(db, room_ids, move_list)

    if not matching_room_ids:
        empty = OpeningStatsResponse(
            total_games=0, white_wins=0, black_wins=0, draws=0, next_moves=[]
        )
        return ResponseEnvelope(data=empty)

    # Tính thống kê
    white_wins = sum(1 for rid in matching_room_ids if room_results.get(rid) == "white_win")
    black_wins = sum(1 for rid in matching_room_ids if room_results.get(rid) == "black_win")
    draws = sum(1 for rid in matching_room_ids if room_results.get(rid) == "draw")
    total = len(matching_room_ids)

    # Tìm next moves (move ở vị trí depth+1)
    next_moves = await _get_next_moves(db, matching_room_ids, depth + 1, room_results)

    stats = OpeningStatsResponse(
        total_games=total, white_wins=white_wins,
        black_wins=black_wins, draws=draws, next_moves=next_moves,
    )
    return ResponseEnvelope(data=stats)


async def _filter_rooms_by_moves(
    db: AsyncSession, room_ids: list, move_list: list[str]
) -> list:
    """Lọc rooms có đúng chuỗi nước đi đầu tiên."""
    if not move_list:
        return room_ids

    matching = set(room_ids)
    for idx, expected_move in enumerate(move_list, start=1):
        query = (
            select(MoveHistory.room_id)
            .where(
                MoveHistory.room_id.in_(matching),
                MoveHistory.move_number == idx,
                MoveHistory.notation == expected_move,
            )
        )
        result = await db.execute(query)
        matching = {r[0] for r in result.all()}
        if not matching:
            return []
    return list(matching)


async def _get_next_moves(
    db: AsyncSession, room_ids: list, move_number: int, room_results: dict
) -> list[NextMoveStats]:
    """Lấy thống kê nước đi tiếp theo."""
    query = (
        select(MoveHistory.room_id, MoveHistory.notation)
        .where(
            MoveHistory.room_id.in_(room_ids),
            MoveHistory.move_number == move_number,
        )
    )
    result = await db.execute(query)
    rows = result.all()

    # Group by notation
    move_data: dict[str, list] = {}
    for room_id, notation in rows:
        move_data.setdefault(notation, []).append(room_id)

    next_moves = []
    for move, rids in sorted(move_data.items(), key=lambda x: -len(x[1])):
        count = len(rids)
        w = sum(1 for rid in rids if room_results.get(rid) == "white_win")
        b = sum(1 for rid in rids if room_results.get(rid) == "black_win")
        d = sum(1 for rid in rids if room_results.get(rid) == "draw")
        next_moves.append(NextMoveStats(
            move=move, count=count,
            win_rate_white=round(w / count * 100, 1) if count else 0,
            draw_rate=round(d / count * 100, 1) if count else 0,
            win_rate_black=round(b / count * 100, 1) if count else 0,
        ))
    return next_moves[:20]  # Top 20 moves
