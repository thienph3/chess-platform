from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.ratings.repository import RatingRepository
from app.modules.ratings.service import RatingService


def get_rating_repository(db: AsyncSession = Depends(get_db)) -> RatingRepository:
    return RatingRepository(db)


def get_rating_service(
    repo: RatingRepository = Depends(get_rating_repository),
) -> RatingService:
    return RatingService(repo)
