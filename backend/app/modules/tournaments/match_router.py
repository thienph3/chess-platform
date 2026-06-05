import uuid

from fastapi import APIRouter, Depends

from app.modules.tournaments.dependencies import get_tournament_service
from app.modules.tournaments.schemas import MatchResponse, MatchResultUpdate
from app.modules.tournaments.service import TournamentService
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.patch("/{match_id}/result", response_model=ResponseEnvelope[MatchResponse])
async def update_match_result(
    match_id: uuid.UUID,
    data: MatchResultUpdate,
    service: TournamentService = Depends(get_tournament_service),
):
    match = await service.update_match_result(match_id, data)
    return ResponseEnvelope(data=match, message="Cập nhật kết quả ván đấu thành công")
