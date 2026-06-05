"""Attendance dependencies — DI providers."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.attendance.repository import AttendanceRepository
from app.modules.attendance.service import AttendanceService


def get_attendance_repository(db: AsyncSession = Depends(get_db)) -> AttendanceRepository:
    return AttendanceRepository(db)


def get_attendance_service(
    repo: AttendanceRepository = Depends(get_attendance_repository),
) -> AttendanceService:
    return AttendanceService(repo)
