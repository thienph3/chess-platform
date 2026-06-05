"""Attendance repository — database queries."""
import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendance.models import Attendance


class AttendanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, attendance: Attendance) -> Attendance:
        self.db.add(attendance)
        await self.db.commit()
        await self.db.refresh(attendance)
        return attendance

    async def get_by_member(self, member_id: uuid.UUID) -> list[Attendance]:
        query = (
            select(Attendance)
            .where(Attendance.member_id == member_id, Attendance.is_deleted.is_(False))
            .order_by(Attendance.date.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_date(self, target_date: date) -> list[Attendance]:
        query = (
            select(Attendance)
            .where(Attendance.date == target_date, Attendance.is_deleted.is_(False))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_today_by_member(self, member_id: uuid.UUID, today: date) -> Attendance | None:
        query = (
            select(Attendance)
            .where(
                Attendance.member_id == member_id,
                Attendance.date == today,
                Attendance.is_deleted.is_(False),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
