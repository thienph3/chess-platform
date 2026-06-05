"""Season service — business logic."""
import uuid

from app.core.exceptions import AppException, NotFoundException
from app.modules.seasons.models import Season
from app.modules.seasons.repository import SeasonRepository
from app.modules.seasons.schemas import SeasonCreate, SeasonResponse


class SeasonService:
    def __init__(self, repository: SeasonRepository):
        self.repository = repository

    async def create_season(self, data: SeasonCreate) -> SeasonResponse:
        if data.start_date >= data.end_date:
            raise AppException("Ngày bắt đầu phải trước ngày kết thúc", status_code=400)
        season = Season(
            name=data.name,
            start_date=data.start_date,
            end_date=data.end_date,
            game_type=data.game_type,
            is_active=True,
        )
        season = await self.repository.create(season)
        return SeasonResponse.model_validate(season)

    async def get_seasons(self) -> list[SeasonResponse]:
        seasons = await self.repository.get_all()
        return [SeasonResponse.model_validate(s) for s in seasons]

    async def get_active_season(self, game_type: str | None = None) -> SeasonResponse | None:
        season = await self.repository.get_active_season(game_type)
        if not season:
            return None
        return SeasonResponse.model_validate(season)

    async def close_season(self, season_id: uuid.UUID) -> SeasonResponse:
        season = await self.repository.get_by_id(season_id)
        if not season:
            raise NotFoundException("Mùa giải không tồn tại")
        if not season.is_active:
            raise AppException("Mùa giải đã đóng", status_code=400)
        season = await self.repository.close_season(season)
        return SeasonResponse.model_validate(season)
