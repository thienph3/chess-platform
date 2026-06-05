"""Season dependencies — DI providers."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.seasons.repository import SeasonRepository
from app.modules.seasons.service import SeasonService


def get_season_repository(db: AsyncSession = Depends(get_db)) -> SeasonRepository:
    return SeasonRepository(db)


def get_season_service(repo: SeasonRepository = Depends(get_season_repository)) -> SeasonService:
    return SeasonService(repo)
