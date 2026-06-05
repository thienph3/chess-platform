import uuid

from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import UserResponse
from app.modules.gallery.dependencies import get_gallery_service
from app.modules.gallery.schemas import GalleryImageResponse, GalleryImageUpdate
from app.modules.gallery.service import GalleryService
from app.shared.schemas import PaginatedResponse, ResponseEnvelope

router = APIRouter(prefix="/gallery", tags=["Gallery"])


@router.get("", response_model=PaginatedResponse[GalleryImageResponse])
async def list_images(
    page: int = 1,
    page_size: int = 20,
    tournament_id: uuid.UUID | None = Query(default=None),
    service: GalleryService = Depends(get_gallery_service),
):
    images, total = await service.list_images(page, page_size, tournament_id)
    return PaginatedResponse(data=images, total=total, page=page, page_size=page_size)


@router.post("", response_model=ResponseEnvelope[GalleryImageResponse], status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    description: str | None = Form(default=None),
    tournament_id: uuid.UUID | None = Form(default=None),
    current_user: UserResponse = Depends(get_current_user),
    service: GalleryService = Depends(get_gallery_service),
):
    image = await service.upload_image(
        file=file, title=title, description=description,
        tournament_id=tournament_id, uploaded_by=current_user.member_id,
    )
    return ResponseEnvelope(data=image, message="Tải ảnh lên thành công")


@router.patch("/{image_id}", response_model=ResponseEnvelope[GalleryImageResponse])
async def update_image(
    image_id: uuid.UUID,
    data: GalleryImageUpdate,
    service: GalleryService = Depends(get_gallery_service),
):
    image = await service.update_image(image_id, data)
    return ResponseEnvelope(data=image, message="Cập nhật ảnh thành công")


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(
    image_id: uuid.UUID,
    service: GalleryService = Depends(get_gallery_service),
):
    await service.delete_image(image_id)
