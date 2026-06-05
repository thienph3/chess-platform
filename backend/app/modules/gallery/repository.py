import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.gallery.models import GalleryImage


class GalleryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, page: int = 1, page_size: int = 20, tournament_id: uuid.UUID | None = None):
        offset = (page - 1) * page_size
        query = select(GalleryImage).where(GalleryImage.is_deleted.is_(False))
        count_query = select(func.count()).select_from(GalleryImage).where(GalleryImage.is_deleted.is_(False))

        if tournament_id:
            query = query.where(GalleryImage.tournament_id == tournament_id)
            count_query = count_query.where(GalleryImage.tournament_id == tournament_id)

        query = query.order_by(GalleryImage.created_at.desc()).offset(offset).limit(page_size)
        result = await self.db.execute(query)
        images = list(result.scalars().all())
        total = (await self.db.execute(count_query)).scalar() or 0
        return images, total

    async def create(self, image: GalleryImage) -> GalleryImage:
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def get_by_id(self, image_id: uuid.UUID) -> GalleryImage | None:
        query = select(GalleryImage).where(GalleryImage.id == image_id, GalleryImage.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, image: GalleryImage) -> GalleryImage:
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def soft_delete(self, image: GalleryImage) -> None:
        image.is_deleted = True
        await self.db.commit()
