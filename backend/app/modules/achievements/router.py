"""Achievement router — API endpoints."""
import uuid

from fastapi import APIRouter, Depends

from app.modules.achievements.dependencies import get_achievement_service
from app.modules.achievements.schemas import AchievementResponse, MemberAchievementResponse
from app.modules.achievements.service import AchievementService
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/achievements", tags=["Achievements"])


@router.get("", response_model=ResponseEnvelope[list[AchievementResponse]])
async def get_all_achievements(
    service: AchievementService = Depends(get_achievement_service),
):
    achievements = await service.get_all_achievements()
    return ResponseEnvelope(data=achievements)


@router.get("/member/{member_id}", response_model=ResponseEnvelope[list[MemberAchievementResponse]])
async def get_member_achievements(
    member_id: uuid.UUID,
    service: AchievementService = Depends(get_achievement_service),
):
    records = await service.get_member_achievements(member_id)
    return ResponseEnvelope(data=records)
