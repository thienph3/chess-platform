"""Season repository — database queries."""
import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.seasons.models import Season


class SeasonRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, season: Season) -> Season:
        self.db.add(season)
        await self.db.commit()
        await self.db.refresh(season)
        return season

    async def get_all(self) -> list[Season]:
        query = (
            select(Season)
            .where(Season.is_deleted.is_(False))
            .order_by(Season.start_date.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, season_id: uuid.UUID) -> Season | None:
        query = select(Season).where(Season.id == season_id, Season.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_season(self, game_type: str | None = None) -> Season | None:
        query = select(Season).where(Season.is_active.is_(True), Season.is_deleted.is_(False))
        if game_type:
            query = query.where(Season.game_type == game_type)
        query = query.order_by(Season.start_date.desc())
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def close_season(self, season: Season) -> Season:
        season.is_active = False
        await self.db.commit()
        await self.db.refresh(season)
        return season
