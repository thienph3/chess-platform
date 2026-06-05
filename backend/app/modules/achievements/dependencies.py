"""Achievement dependencies — DI providers."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.achievements.repository import AchievementRepository
from app.modules.achievements.service import AchievementService


def get_achievement_repository(db: AsyncSession = Depends(get_db)) -> AchievementRepository:
    return AchievementRepository(db)


def get_achievement_service(
    repo: AchievementRepository = Depends(get_achievement_repository),
) -> AchievementService:
    return AchievementService(repo)
