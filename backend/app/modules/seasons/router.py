"""Season router — API endpoints."""
import uuid

from fastapi import APIRouter, Depends, Query, status

from app.modules.seasons.dependencies import get_season_service
from app.modules.seasons.schemas import SeasonCreate, SeasonResponse
from app.modules.seasons.service import SeasonService
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/seasons", tags=["Seasons"])


@router.get("", response_model=ResponseEnvelope[list[SeasonResponse]])
async def get_seasons(service: SeasonService = Depends(get_season_service)):
    seasons = await service.get_seasons()
    return ResponseEnvelope(data=seasons)


@router.post("", response_model=ResponseEnvelope[SeasonResponse], status_code=status.HTTP_201_CREATED)
async def create_season(
    data: SeasonCreate,
    service: SeasonService = Depends(get_season_service),
):
    season = await service.create_season(data)
    return ResponseEnvelope(data=season, message="Tạo mùa giải thành công")


@router.get("/active", response_model=ResponseEnvelope[SeasonResponse | None])
async def get_active_season(
    game_type: str | None = Query(None),
    service: SeasonService = Depends(get_season_service),
):
    season = await service.get_active_season(game_type)
    return ResponseEnvelope(data=season)


@router.patch("/{season_id}/close", response_model=ResponseEnvelope[SeasonResponse])
async def close_season(
    season_id: uuid.UUID,
    service: SeasonService = Depends(get_season_service),
):
    season = await service.close_season(season_id)
    return ResponseEnvelope(data=season, message="Đã đóng mùa giải")
