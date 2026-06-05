import uuid

from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_current_admin_user
from app.modules.news.dependencies import get_news_service
from app.modules.news.schemas import NewsPostCreate, NewsPostResponse
from app.modules.news.service import NewsService
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/news", tags=["News"])


@router.get("", response_model=ResponseEnvelope[list[NewsPostResponse]])
async def list_news(
    limit: int = 50,
    service: NewsService = Depends(get_news_service),
):
    data = await service.get_all(limit)
    return ResponseEnvelope(data=data, message="Danh sách tin tức")


@router.post(
    "",
    response_model=ResponseEnvelope[NewsPostResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_news(
    data: NewsPostCreate,
    current_user=Depends(get_current_admin_user),
    service: NewsService = Depends(get_news_service),
):
    post = await service.create(data, author_id=current_user.id)
    return ResponseEnvelope(data=post, message="Đăng tin thành công")


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(
    post_id: uuid.UUID,
    current_user=Depends(get_current_admin_user),
    service: NewsService = Depends(get_news_service),
):
    await service.delete(post_id)
