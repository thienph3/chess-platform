"""Achievement service — business logic."""
import uuid

from app.modules.achievements.repository import AchievementRepository
from app.modules.achievements.schemas import AchievementResponse, MemberAchievementResponse


class AchievementService:
    def __init__(self, repository: AchievementRepository):
        self.repository = repository

    async def get_all_achievements(self) -> list[AchievementResponse]:
        achievements = await self.repository.get_all_achievements()
        return [AchievementResponse.model_validate(a) for a in achievements]

    async def get_member_achievements(self, member_id: uuid.UUID) -> list[MemberAchievementResponse]:
        records = await self.repository.get_member_achievements(member_id)
        return [MemberAchievementResponse.model_validate(r) for r in records]

    async def check_and_award(self, member_id: uuid.UUID) -> list[MemberAchievementResponse]:
        """Kiểm tra điều kiện và trao huy hiệu mới."""
        all_achievements = await self.repository.get_all_achievements()
        earned_ids = await self.repository.get_member_achievement_ids(member_id)
        newly_awarded: list[MemberAchievementResponse] = []

        for achievement in all_achievements:
            if achievement.id in earned_ids:
                continue
            # Logic kiểm tra điều kiện (mở rộng sau)
            # Hiện tại chỉ award nếu condition_type == "manual"
            if achievement.condition_type == "manual":
                continue
            # Placeholder: các condition khác sẽ được implement khi tích hợp
        return newly_awarded
