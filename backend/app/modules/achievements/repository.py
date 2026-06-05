"""Achievement repository — database queries."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.achievements.models import Achievement, MemberAchievement


class AchievementRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_achievements(self) -> list[Achievement]:
        query = select(Achievement).where(Achievement.is_deleted.is_(False))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_member_achievements(self, member_id: uuid.UUID) -> list[MemberAchievement]:
        query = (
            select(MemberAchievement)
            .where(MemberAchievement.member_id == member_id, MemberAchievement.is_deleted.is_(False))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_member_achievement_ids(self, member_id: uuid.UUID) -> set[uuid.UUID]:
        query = (
            select(MemberAchievement.achievement_id)
            .where(MemberAchievement.member_id == member_id, MemberAchievement.is_deleted.is_(False))
        )
        result = await self.db.execute(query)
        return {row[0] for row in result.all()}

    async def award_achievement(self, member_id: uuid.UUID, achievement_id: uuid.UUID) -> MemberAchievement:
        ma = MemberAchievement(member_id=member_id, achievement_id=achievement_id)
        self.db.add(ma)
        await self.db.commit()
        await self.db.refresh(ma)
        return ma
