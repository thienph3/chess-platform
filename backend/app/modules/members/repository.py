import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.members.models import Member


class MemberRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, page: int = 1, page_size: int = 20, search: str | None = None) -> tuple[list[Member], int]:
        offset = (page - 1) * page_size
        query = select(Member).where(Member.is_deleted.is_(False))
        count_query = select(func.count()).select_from(Member).where(Member.is_deleted.is_(False))

        if search:
            search_filter = Member.full_name.ilike(f"%{search}%")
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        query = query.order_by(Member.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        members = list(result.scalars().all())

        total = (await self.db.execute(count_query)).scalar() or 0
        return members, total

    async def get_by_id(self, member_id: uuid.UUID) -> Member | None:
        query = select(Member).where(Member.id == member_id, Member.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, member: Member) -> Member:
        self.db.add(member)
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def update(self, member: Member) -> Member:
        await self.db.commit()
        await self.db.refresh(member)
        return member

    async def soft_delete(self, member: Member) -> None:
        member.is_deleted = True
        await self.db.commit()
