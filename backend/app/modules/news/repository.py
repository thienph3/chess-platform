import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.news.models import NewsPost


class NewsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int = 50) -> list[NewsPost]:
        query = (
            select(NewsPost)
            .where(NewsPost.is_deleted.is_(False))
            .order_by(NewsPost.is_pinned.desc(), NewsPost.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, post: NewsPost) -> NewsPost:
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def delete(self, post_id: uuid.UUID) -> bool:
        query = select(NewsPost).where(
            NewsPost.id == post_id, NewsPost.is_deleted.is_(False)
        )
        result = await self.db.execute(query)
        post = result.scalar_one_or_none()
        if not post:
            return False
        post.is_deleted = True
        await self.db.commit()
        return True
