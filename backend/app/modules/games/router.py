import uuid

from fastapi import APIRouter, Depends, status

from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import UserResponse
from app.modules.games.dependencies import get_game_service
from app.modules.games.schemas import GameRoomCreate, GameRoomResponse, ImportGameRequest, MoveHistoryResponse
from app.modules.games.service import GameService
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/games", tags=["Games"])


@router.post("", response_model=ResponseEnvelope[GameRoomResponse], status_code=status.HTTP_201_CREATED)
async def create_game_room(
    data: GameRoomCreate,
    current_user: UserResponse = Depends(get_current_user),
    service: GameService = Depends(get_game_service),
):
    room = await service.create_room(current_user.member_id, data)
    return ResponseEnvelope(data=room, message="Tạo phòng chơi thành công")


@router.post("/import", response_model=ResponseEnvelope[GameRoomResponse], status_code=status.HTTP_201_CREATED)
async def import_game(
    data: ImportGameRequest,
    service: GameService = Depends(get_game_service),
):
    """Import ván đấu đã chơi offline hoặc nhập kết quả thủ công."""
    room = await service.import_game(data)
    return ResponseEnvelope(data=room, message="Import ván đấu thành công")


@router.get("/live", response_model=ResponseEnvelope[list[GameRoomResponse]])
async def get_live_games(service: GameService = Depends(get_game_service)):
    rooms = await service.get_live_rooms()
    return ResponseEnvelope(data=rooms)


@router.get("/{room_id}", response_model=ResponseEnvelope[GameRoomResponse])
async def get_game_room(room_id: uuid.UUID, service: GameService = Depends(get_game_service)):
    room = await service.get_room(room_id)
    return ResponseEnvelope(data=room)


@router.post("/{room_id}/join", response_model=ResponseEnvelope[GameRoomResponse])
async def join_game_room(
    room_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: GameService = Depends(get_game_service),
):
    room = await service.join_room(room_id, current_user.member_id)
    return ResponseEnvelope(data=room, message="Tham gia phòng thành công")


@router.post("/{room_id}/cancel", response_model=ResponseEnvelope[GameRoomResponse])
async def cancel_game_room(
    room_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    service: GameService = Depends(get_game_service),
):
    """Hủy phòng: nếu chưa có đối thủ → hủy bình thường, nếu đang chơi → tự động đầu hàng."""
    room = await service.cancel_room(room_id, current_user.member_id)
    return ResponseEnvelope(data=room, message="Đã hủy phòng")


@router.post("/from-match/{match_id}", response_model=ResponseEnvelope[GameRoomResponse], status_code=status.HTTP_201_CREATED)
async def create_room_from_match(
    match_id: uuid.UUID,
    service: GameService = Depends(get_game_service),
):
    """Tạo phòng chơi từ ván đấu trong giải (tournament integration)."""
    room = await service.create_room_from_match(match_id)
    return ResponseEnvelope(data=room, message="Tạo phòng từ ván đấu thành công")


@router.get("/{room_id}/moves", response_model=ResponseEnvelope[list[MoveHistoryResponse]])
async def get_game_moves(room_id: uuid.UUID, service: GameService = Depends(get_game_service)):
    moves = await service.get_moves(room_id)
    return ResponseEnvelope(data=moves)


@router.post("/{room_id}/review", response_model=ResponseEnvelope[GameRoomResponse])
async def review_game(
    room_id: uuid.UUID,
    service: GameService = Depends(get_game_service),
):
    """Chấm điểm ván đấu bằng engine (gọi Analysis service)."""
    room = await service.review_game(room_id)
    return ResponseEnvelope(data=room, message="Chấm điểm ván đấu thành công")


@router.get("/history/all", response_model=ResponseEnvelope[list[GameRoomResponse]])
async def get_finished_games(
    limit: int = 50,
    service: GameService = Depends(get_game_service),
):
    """Danh sách ván đấu đã kết thúc (public, hiển thị accuracy)."""
    rooms = await service.get_finished_games(limit)
    return ResponseEnvelope(data=rooms)


@router.get("/{room_id}/export/pgn")
async def export_pgn(
    room_id: uuid.UUID,
    service: GameService = Depends(get_game_service),
):
    """Export ván đấu dạng PGN (Chess) hoặc text notation."""
    from fastapi.responses import PlainTextResponse

    pgn_content = await service.export_pgn(room_id)
    return PlainTextResponse(
        content=pgn_content,
        media_type="application/x-chess-pgn",
        headers={"Content-Disposition": f"attachment; filename=game_{room_id}.pgn"},
    )
