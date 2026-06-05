"""Attendance service — business logic."""
import uuid
from datetime import date, timedelta

from app.core.exceptions import AppException
from app.modules.attendance.models import Attendance, EventType
from app.modules.attendance.repository import AttendanceRepository
from app.modules.attendance.schemas import AttendanceCreate, AttendanceResponse, AttendanceSummary


class AttendanceService:
    def __init__(self, repository: AttendanceRepository):
        self.repository = repository

    async def check_in(self, member_id: uuid.UUID, data: AttendanceCreate) -> AttendanceResponse:
        today = date.today()
        existing = await self.repository.get_today_by_member(member_id, today)
        if existing:
            raise AppException("Bạn đã điểm danh hôm nay rồi", status_code=400)

        attendance = Attendance(
            member_id=member_id,
            date=today,
            event_type=EventType(data.event_type),
            notes=data.notes,
        )
        attendance = await self.repository.create(attendance)
        return AttendanceResponse.model_validate(attendance)

    async def get_member_attendance(self, member_id: uuid.UUID) -> list[AttendanceResponse]:
        records = await self.repository.get_by_member(member_id)
        return [AttendanceResponse.model_validate(r) for r in records]

    async def get_attendance_summary(self, member_id: uuid.UUID) -> AttendanceSummary:
        records = await self.repository.get_by_member(member_id)
        total_sessions = len(records)

        if not records:
            return AttendanceSummary(total_sessions=0, current_streak=0, last_attendance=None)

        # Tính streak liên tục
        dates = sorted({r.date for r in records}, reverse=True)
        streak = 1
        for i in range(1, len(dates)):
            if dates[i - 1] - dates[i] == timedelta(days=1):
                streak += 1
            else:
                break

        return AttendanceSummary(
            total_sessions=total_sessions,
            current_streak=streak,
            last_attendance=dates[0],
        )
