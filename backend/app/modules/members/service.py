import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.exceptions import NotFoundException
from app.modules.members.models import Member
from app.modules.members.repository import MemberRepository
from app.modules.members.schemas import MemberCreate, MemberResponse, MemberUpdate

UPLOAD_DIR = Path("uploads/avatars")


class MemberService:
    def __init__(self, repository: MemberRepository):
        self.repository = repository

    async def list_members(self, page: int, page_size: int, search: str | None = None) -> tuple[list[MemberResponse], int]:
        members, total = await self.repository.get_all(page, page_size, search)
        return [MemberResponse.model_validate(m) for m in members], total

    async def get_member(self, member_id: uuid.UUID) -> MemberResponse:
        member = await self.repository.get_by_id(member_id)
        if not member:
            raise NotFoundException("Thành viên không tồn tại")
        return MemberResponse.model_validate(member)

    async def create_member(self, data: MemberCreate) -> MemberResponse:
        member = Member(**data.model_dump())
        member = await self.repository.create(member)
        return MemberResponse.model_validate(member)

    async def update_member(self, member_id: uuid.UUID, data: MemberUpdate) -> MemberResponse:
        member = await self.repository.get_by_id(member_id)
        if not member:
            raise NotFoundException("Thành viên không tồn tại")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(member, field, value)
        member = await self.repository.update(member)
        return MemberResponse.model_validate(member)

    async def delete_member(self, member_id: uuid.UUID) -> None:
        member = await self.repository.get_by_id(member_id)
        if not member:
            raise NotFoundException("Thành viên không tồn tại")
        await self.repository.soft_delete(member)

    async def upload_avatar(self, member_id: uuid.UUID, file: UploadFile) -> MemberResponse:
        member = await self.repository.get_by_id(member_id)
        if not member:
            raise NotFoundException("Thành viên không tồn tại")

        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        ext = Path(file.filename or "avatar.png").suffix
        filename = f"{member_id}{ext}"
        filepath = UPLOAD_DIR / filename

        content = await file.read()
        filepath.write_bytes(content)

        member.avatar_url = f"/uploads/avatars/{filename}"
        member = await self.repository.update(member)
        return MemberResponse.model_validate(member)
