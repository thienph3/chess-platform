import uuid

from app.core.exceptions import NotFoundException
from app.modules.news.models import NewsPost
from app.modules.news.repository import NewsRepository
from app.modules.news.schemas import NewsPostCreate, NewsPostResponse


class NewsService:
    def __init__(self, repository: NewsRepository):
        self.repository = repository

    async def get_all(self, limit: int = 50) -> list[NewsPostResponse]:
        posts = await self.repository.get_all(limit)
        return [NewsPostResponse.model_validate(p) for p in posts]

    async def create(
        self, data: NewsPostCreate, author_id: uuid.UUID
    ) -> NewsPostResponse:
        post = NewsPost(
            title=data.title,
            content=data.content,
            is_pinned=data.is_pinned,
            author_id=author_id,
        )
        post = await self.repository.create(post)
        return NewsPostResponse.model_validate(post)

    async def delete(self, post_id: uuid.UUID) -> None:
        deleted = await self.repository.delete(post_id)
        if not deleted:
            raise NotFoundException("Bài viết không tồn tại")
