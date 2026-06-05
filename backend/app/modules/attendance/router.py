"""Attendance router — API endpoints."""
import uuid

from fastapi import APIRouter, Depends, status

from app.modules.attendance.dependencies import get_attendance_service
from app.modules.attendance.schemas import AttendanceCreate, AttendanceResponse, AttendanceSummary
from app.modules.attendance.service import AttendanceService
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import UserResponse
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/check-in", response_model=ResponseEnvelope[AttendanceResponse], status_code=status.HTTP_201_CREATED)
async def check_in(
    data: AttendanceCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: AttendanceService = Depends(get_attendance_service),
):
    result = await service.check_in(current_user.member_id, data)
    return ResponseEnvelope(data=result, message="Điểm danh thành công")


@router.get("/member/{member_id}", response_model=ResponseEnvelope[list[AttendanceResponse]])
async def get_member_attendance(
    member_id: uuid.UUID,
    service: AttendanceService = Depends(get_attendance_service),
):
    records = await service.get_member_attendance(member_id)
    return ResponseEnvelope(data=records)


@router.get("/summary/{member_id}", response_model=ResponseEnvelope[AttendanceSummary])
async def get_attendance_summary(
    member_id: uuid.UUID,
    service: AttendanceService = Depends(get_attendance_service),
):
    summary = await service.get_attendance_summary(member_id)
    return ResponseEnvelope(data=summary)
