import uuid

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.modules.members.dependencies import get_member_service
from app.modules.members.schemas import MemberCreate, MemberResponse, MemberUpdate
from app.modules.members.service import MemberService
from app.shared.schemas import PaginatedResponse, ResponseEnvelope

router = APIRouter(prefix="/members", tags=["Members"])


@router.get("", response_model=PaginatedResponse[MemberResponse])
async def list_members(
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    service: MemberService = Depends(get_member_service),
):
    members, total = await service.list_members(page, page_size, search)
    return PaginatedResponse(data=members, total=total, page=page, page_size=page_size)


@router.get("/{member_id}", response_model=ResponseEnvelope[MemberResponse])
async def get_member(
    member_id: uuid.UUID,
    service: MemberService = Depends(get_member_service),
):
    member = await service.get_member(member_id)
    return ResponseEnvelope(data=member)


@router.post("", response_model=ResponseEnvelope[MemberResponse], status_code=status.HTTP_201_CREATED)
async def create_member(
    data: MemberCreate,
    service: MemberService = Depends(get_member_service),
):
    member = await service.create_member(data)
    return ResponseEnvelope(data=member, message="Tạo thành viên thành công")


@router.patch("/{member_id}", response_model=ResponseEnvelope[MemberResponse])
async def update_member(
    member_id: uuid.UUID,
    data: MemberUpdate,
    service: MemberService = Depends(get_member_service),
):
    member = await service.update_member(member_id, data)
    return ResponseEnvelope(data=member, message="Cập nhật thành viên thành công")


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: uuid.UUID,
    service: MemberService = Depends(get_member_service),
):
    await service.delete_member(member_id)


@router.post("/{member_id}/avatar", response_model=ResponseEnvelope[MemberResponse])
async def upload_avatar(
    member_id: uuid.UUID,
    file: UploadFile = File(...),
    service: MemberService = Depends(get_member_service),
):
    member = await service.upload_avatar(member_id, file)
    return ResponseEnvelope(data=member, message="Cập nhật ảnh đại diện thành công")
