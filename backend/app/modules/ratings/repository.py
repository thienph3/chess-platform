import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.modules.ratings.models import Rating, RatingChange
from app.modules.tournaments.models import GameType, Match, TimeFormat, TournamentRound


class RatingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_leaderboard(
        self, game_type: GameType, time_format: TimeFormat, limit: int = 20
    ) -> list[Rating]:
        query = (
            select(Rating)
            .where(
                Rating.game_type == game_type,
                Rating.time_format == time_format,
                Rating.is_deleted.is_(False),
            )
            .order_by(Rating.rating.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_ratings_by_member(self, member_id: uuid.UUID) -> list[Rating]:
        query = select(Rating).where(
            Rating.member_id == member_id, Rating.is_deleted.is_(False)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_rating(
        self, member_id: uuid.UUID, game_type: GameType, time_format: TimeFormat
    ) -> Rating | None:
        query = select(Rating).where(
            Rating.member_id == member_id,
            Rating.game_type == game_type,
            Rating.time_format == time_format,
            Rating.is_deleted.is_(False),
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_rating(self, rating: Rating) -> Rating:
        self.db.add(rating)
        await self.db.flush()
        return rating

    async def get_history(
        self, member_id: uuid.UUID, game_type: GameType, time_format: TimeFormat
    ) -> list[RatingChange]:
        query = (
            select(RatingChange)
            .join(Rating, RatingChange.rating_id == Rating.id)
            .where(
                Rating.member_id == member_id,
                Rating.game_type == game_type,
                Rating.time_format == time_format,
                RatingChange.is_deleted.is_(False),
            )
            .order_by(RatingChange.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_match_by_id(self, match_id: uuid.UUID) -> Match | None:
        query = (
            select(Match)
            .options(joinedload(Match.round).joinedload(TournamentRound.tournament))
            .where(Match.id == match_id, Match.is_deleted.is_(False))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_rating_change(self, change: RatingChange) -> RatingChange:
        self.db.add(change)
        await self.db.flush()
        return change

    async def commit(self) -> None:
        await self.db.commit()
