from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.members.repository import MemberRepository
from app.modules.members.service import MemberService


def get_member_repository(db: AsyncSession = Depends(get_db)) -> MemberRepository:
    return MemberRepository(db)


def get_member_service(repo: MemberRepository = Depends(get_member_repository)) -> MemberService:
    return MemberService(repo)
