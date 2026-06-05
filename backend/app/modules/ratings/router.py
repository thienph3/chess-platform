import uuid

from fastapi import APIRouter, Depends, Query

from app.modules.ratings.dependencies import get_rating_service
from app.modules.ratings.schemas import (
    CalculateRequest,
    CalculateResponse,
    LeaderboardEntry,
    RatingChangeResponse,
    RatingResponse,
)
from app.modules.ratings.service import RatingService
from app.modules.tournaments.models import GameType, TimeFormat
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/ratings", tags=["Ratings"])
leaderboard_router = APIRouter(prefix="/leaderboard", tags=["Ratings"])


@leaderboard_router.get("", response_model=ResponseEnvelope[list[LeaderboardEntry]])
async def get_leaderboard(
    game_type: GameType = Query(...),
    time_format: TimeFormat = Query(...),
    limit: int = Query(20, ge=1, le=100),
    service: RatingService = Depends(get_rating_service),
):
    data = await service.get_leaderboard(game_type, time_format, limit)
    return ResponseEnvelope(data=data, message="Bảng xếp hạng")


@router.post("/calculate", response_model=ResponseEnvelope[CalculateResponse])
async def calculate_rating(
    body: CalculateRequest,
    service: RatingService = Depends(get_rating_service),
):
    if not body.rated:
        return ResponseEnvelope(data=None, message="Ván đấu không tính ELO (unrated)")
    result = await service.calculate_match_rating(body.match_id)
    return ResponseEnvelope(data=result, message="Tính ELO thành công")


@router.get("/{member_id}", response_model=ResponseEnvelope[list[RatingResponse]])
async def get_member_ratings(
    member_id: uuid.UUID,
    service: RatingService = Depends(get_rating_service),
):
    data = await service.get_member_ratings(member_id)
    return ResponseEnvelope(data=data)


@router.get(
    "/{member_id}/history",
    response_model=ResponseEnvelope[list[RatingChangeResponse]],
)
async def get_rating_history(
    member_id: uuid.UUID,
    game_type: GameType = Query(...),
    time_format: TimeFormat = Query(...),
    service: RatingService = Depends(get_rating_service),
):
    data = await service.get_rating_history(member_id, game_type, time_format)
    return ResponseEnvelope(data=data, message="Lịch sử thay đổi ELO")


@router.get(
    "/{member_id}/rank-history",
    response_model=ResponseEnvelope[list],
)
async def get_rank_history(
    member_id: uuid.UUID,
    service: RatingService = Depends(get_rating_service),
):
    """Lịch sử xếp hạng theo thời gian (placeholder — cần periodic snapshots)."""
    # TODO: Implement periodic rank snapshots
    return ResponseEnvelope(data=[], message="Lịch sử xếp hạng")
