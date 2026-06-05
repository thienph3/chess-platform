import uuid

from fastapi import APIRouter, Depends, status

from app.modules.tournaments.dependencies import get_tournament_service
from app.modules.tournaments.models import GameType, TournamentStatus
from app.modules.tournaments.schemas import (
    ParticipantCreate,
    ParticipantResponse,
    RoundCreate,
    RoundResponse,
    StandingsEntry,
    TournamentCreate,
    TournamentPrizeCreate,
    TournamentPrizeResponse,
    TournamentResponse,
    TournamentUpdate,
)
from app.modules.tournaments.service import TournamentService
from app.shared.schemas import PaginatedResponse, ResponseEnvelope

router = APIRouter(prefix="/tournaments", tags=["Tournaments"])


@router.get("", response_model=PaginatedResponse[TournamentResponse])
async def list_tournaments(
    page: int = 1,
    page_size: int = 20,
    status_filter: TournamentStatus | None = None,
    game_type: GameType | None = None,
    service: TournamentService = Depends(get_tournament_service),
):
    tournaments, total = await service.list_tournaments(page, page_size, status_filter, game_type)
    return PaginatedResponse(data=tournaments, total=total, page=page, page_size=page_size)


@router.get("/{tournament_id}", response_model=ResponseEnvelope[TournamentResponse])
async def get_tournament(
    tournament_id: uuid.UUID,
    service: TournamentService = Depends(get_tournament_service),
):
    tournament = await service.get_tournament(tournament_id)
    return ResponseEnvelope(data=tournament)


@router.post("", response_model=ResponseEnvelope[TournamentResponse], status_code=status.HTTP_201_CREATED)
async def create_tournament(
    data: TournamentCreate,
    service: TournamentService = Depends(get_tournament_service),
):
    tournament = await service.create_tournament(data)
    return ResponseEnvelope(data=tournament, message="Tạo giải đấu thành công")


@router.patch("/{tournament_id}", response_model=ResponseEnvelope[TournamentResponse])
async def update_tournament(
    tournament_id: uuid.UUID,
    data: TournamentUpdate,
    service: TournamentService = Depends(get_tournament_service),
):
    tournament = await service.update_tournament(tournament_id, data)
    return ResponseEnvelope(data=tournament, message="Cập nhật giải đấu thành công")


@router.delete("/{tournament_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tournament(
    tournament_id: uuid.UUID,
    service: TournamentService = Depends(get_tournament_service),
):
    await service.delete_tournament(tournament_id)


# --- Participants ---

@router.post(
    "/{tournament_id}/participants",
    response_model=ResponseEnvelope[ParticipantResponse],
    status_code=status.HTTP_201_CREATED,
)
async def register_participant(
    tournament_id: uuid.UUID,
    data: ParticipantCreate,
    service: TournamentService = Depends(get_tournament_service),
):
    participant = await service.add_participant(tournament_id, data)
    return ResponseEnvelope(data=participant, message="Đăng ký tham gia thành công")


@router.get("/{tournament_id}/participants", response_model=ResponseEnvelope[list[ParticipantResponse]])
async def list_participants(
    tournament_id: uuid.UUID,
    service: TournamentService = Depends(get_tournament_service),
):
    participants = await service.list_participants(tournament_id)
    return ResponseEnvelope(data=participants)


# --- Rounds ---

@router.post(
    "/{tournament_id}/rounds",
    response_model=ResponseEnvelope[RoundResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_round(
    tournament_id: uuid.UUID,
    data: RoundCreate,
    service: TournamentService = Depends(get_tournament_service),
):
    round_ = await service.create_round(tournament_id, data)
    return ResponseEnvelope(data=round_, message="Tạo vòng đấu thành công")


@router.get("/{tournament_id}/rounds", response_model=ResponseEnvelope[list[RoundResponse]])
async def list_rounds(
    tournament_id: uuid.UUID,
    service: TournamentService = Depends(get_tournament_service),
):
    rounds = await service.list_rounds(tournament_id)
    return ResponseEnvelope(data=rounds)


@router.post("/{tournament_id}/generate-pairings", response_model=ResponseEnvelope[list[RoundResponse]])
async def generate_pairings(
    tournament_id: uuid.UUID,
    service: TournamentService = Depends(get_tournament_service),
):
    rounds = await service.generate_pairings(tournament_id)
    return ResponseEnvelope(data=rounds, message="Tạo cặp đấu thành công")


# --- Standings ---

@router.get("/{tournament_id}/standings", response_model=ResponseEnvelope[list[StandingsEntry]])
async def get_standings(
    tournament_id: uuid.UUID,
    service: TournamentService = Depends(get_tournament_service),
):
    standings = await service.get_standings(tournament_id)
    return ResponseEnvelope(data=standings, message="Bảng xếp hạng giải đấu")


# --- Prizes ---

@router.get("/{tournament_id}/prizes", response_model=ResponseEnvelope[TournamentPrizeResponse])
async def get_prizes(
    tournament_id: uuid.UUID,
    service: TournamentService = Depends(get_tournament_service),
):
    prizes = await service.get_prizes(tournament_id)
    return ResponseEnvelope(data=prizes, message="Danh sách giải thưởng")


@router.post(
    "/{tournament_id}/prizes",
    response_model=ResponseEnvelope[TournamentPrizeResponse],
    status_code=status.HTTP_201_CREATED,
)
async def set_prizes(
    tournament_id: uuid.UUID,
    data: TournamentPrizeCreate,
    service: TournamentService = Depends(get_tournament_service),
):
    prizes = await service.set_prizes(tournament_id, data.prizes)
    return ResponseEnvelope(data=prizes, message="Cập nhật giải thưởng thành công")


@router.post("/{tournament_id}/rounds/{round_id}/create-rooms", response_model=ResponseEnvelope[int])
async def create_rooms_for_round(
    tournament_id: uuid.UUID,
    round_id: uuid.UUID,
    service: TournamentService = Depends(get_tournament_service),
):
    """Tạo game rooms cho tất cả matches trong round (online tournament)."""
    count = await service.create_rooms_for_round(tournament_id, round_id)
    return ResponseEnvelope(data=count, message=f"Đã tạo {count} phòng chơi")
