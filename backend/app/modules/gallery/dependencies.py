from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.gallery.repository import GalleryRepository
from app.modules.gallery.service import GalleryService


def get_gallery_repository(db: AsyncSession = Depends(get_db)) -> GalleryRepository:
    return GalleryRepository(db)


def get_gallery_service(repo: GalleryRepository = Depends(get_gallery_repository)) -> GalleryService:
    return GalleryService(repo)
