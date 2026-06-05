import os
import uuid

from fastapi import UploadFile

from app.core.exceptions import AppException, NotFoundException
from app.modules.gallery.models import GalleryImage
from app.modules.gallery.repository import GalleryRepository
from app.modules.gallery.schemas import GalleryImageResponse, GalleryImageUpdate

UPLOAD_DIR = "uploads/gallery"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


class GalleryService:
    def __init__(self, repository: GalleryRepository):
        self.repository = repository

    async def list_images(
        self, page: int, page_size: int, tournament_id: uuid.UUID | None = None
    ) -> tuple[list[GalleryImageResponse], int]:
        images, total = await self.repository.get_all(page, page_size, tournament_id)
        return [GalleryImageResponse.model_validate(img) for img in images], total

    async def upload_image(
        self, file: UploadFile, title: str | None, description: str | None,
        tournament_id: uuid.UUID | None, uploaded_by: uuid.UUID | None,
    ) -> GalleryImageResponse:
        # Validate file
        ext = os.path.splitext(file.filename or "")[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise AppException(f"Định dạng file không hỗ trợ. Chấp nhận: {', '.join(ALLOWED_EXTENSIONS)}")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise AppException("File quá lớn. Tối đa 5MB.")

        # Save file
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(content)

        url = f"/uploads/gallery/{filename}"
        image = GalleryImage(
            title=title, description=description, filename=filename,
            url=url, tournament_id=tournament_id, uploaded_by=uploaded_by,
        )
        image = await self.repository.create(image)
        return GalleryImageResponse.model_validate(image)

    async def update_image(self, image_id: uuid.UUID, data: GalleryImageUpdate) -> GalleryImageResponse:
        image = await self.repository.get_by_id(image_id)
        if not image:
            raise NotFoundException("Ảnh không tồn tại")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(image, field, value)
        image = await self.repository.update(image)
        return GalleryImageResponse.model_validate(image)

    async def delete_image(self, image_id: uuid.UUID) -> None:
        image = await self.repository.get_by_id(image_id)
        if not image:
            raise NotFoundException("Ảnh không tồn tại")
        await self.repository.soft_delete(image)
