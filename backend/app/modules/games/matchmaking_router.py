"""Matchmaking endpoints — tìm đối thủ tự động."""
import uuid

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import UserResponse
from app.modules.games.matchmaking import (
    add_to_queue,
    find_match,
    is_in_queue,
    remove_from_queue,
)
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/games/matchmaking", tags=["Matchmaking"])


class MatchmakingJoinRequest(BaseModel):
    game_type: str
    time_format: str  # bullet, blitz, rapid, standard
    rating: int = 1200


class MatchmakingStatusResponse(BaseModel):
    in_queue: bool
    matched: bool
    opponent_id: uuid.UUID | None = None
    game_type: str | None = None
    time_format: str | None = None


@router.post("/join", response_model=ResponseEnvelope[MatchmakingStatusResponse])
async def join_matchmaking(
    data: MatchmakingJoinRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """Tham gia hàng đợi tìm trận."""
    member_id = current_user.member_id
    add_to_queue(member_id, data.rating, data.game_type, data.time_format)

    # Thử tìm đối thủ ngay
    opponent = find_match(
        member_id, data.rating, data.game_type, data.time_format
    )
    if opponent:
        result = MatchmakingStatusResponse(
            in_queue=False, matched=True,
            opponent_id=opponent.member_id,
            game_type=data.game_type, time_format=data.time_format,
        )
        return ResponseEnvelope(data=result, message="Đã tìm thấy đối thủ!")

    result = MatchmakingStatusResponse(
        in_queue=True, matched=False,
        game_type=data.game_type, time_format=data.time_format,
    )
    return ResponseEnvelope(data=result, message="Đang tìm đối thủ...")


@router.post("/leave", response_model=ResponseEnvelope[None], status_code=status.HTTP_200_OK)
async def leave_matchmaking(
    data: MatchmakingJoinRequest,
    current_user: UserResponse = Depends(get_current_user),
):
    """Rời khỏi hàng đợi tìm trận."""
    remove_from_queue(current_user.member_id, data.game_type, data.time_format)
    return ResponseEnvelope(data=None, message="Đã rời hàng đợi")


@router.get("/status", response_model=ResponseEnvelope[MatchmakingStatusResponse])
async def matchmaking_status(
    current_user: UserResponse = Depends(get_current_user),
):
    """Kiểm tra trạng thái matchmaking."""
    queue_info = is_in_queue(current_user.member_id)
    if queue_info:
        result = MatchmakingStatusResponse(
            in_queue=True, matched=False,
            game_type=queue_info[0], time_format=queue_info[1],
        )
    else:
        result = MatchmakingStatusResponse(in_queue=False, matched=False)
    return ResponseEnvelope(data=result)
