import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import User


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email, User.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: str | uuid.UUID) -> User | None:
        uid = uuid.UUID(str(user_id))
        query = select(User).where(User.id == uid, User.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_reset_token(self, token: str) -> User | None:
        query = select(User).where(User.reset_token == token, User.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_user(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_user(self, user: User) -> User:
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def list_all_users(self) -> list[User]:
        query = select(User).where(User.is_deleted.is_(False)).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
