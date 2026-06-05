import uuid

from app.core.exceptions import AppException, NotFoundException
from app.modules.games.models import GameRoom, GameRoomStatus, MoveHistory
from app.modules.games.repository import GameRepository
from app.modules.games.schemas import GameRoomCreate, GameRoomResponse, ImportGameRequest, MoveHistoryResponse


class GameService:
    def __init__(self, repository: GameRepository):
        self.repository = repository

    async def create_room(self, creator_id: uuid.UUID, data: GameRoomCreate) -> GameRoomResponse:
        room = GameRoom(
            white_player_id=creator_id,
            black_player_id=data.black_player_id,
            game_type=data.game_type,
            time_control=data.time_control,
            increment=data.increment,
            match_id=data.match_id,
            status=GameRoomStatus.waiting if not data.black_player_id else GameRoomStatus.playing,
        )
        room = await self.repository.create_room(room)
        return GameRoomResponse.model_validate(room)

    async def get_room(self, room_id: uuid.UUID) -> GameRoomResponse:
        room = await self.repository.get_room_by_id(room_id)
        if not room:
            raise NotFoundException("Phòng chơi không tồn tại")
        return GameRoomResponse.model_validate(room)

    async def get_live_rooms(self) -> list[GameRoomResponse]:
        rooms = await self.repository.get_live_rooms()
        return [GameRoomResponse.model_validate(r) for r in rooms]

    async def join_room(self, room_id: uuid.UUID, player_id: uuid.UUID) -> GameRoomResponse:
        room = await self.repository.get_room_by_id(room_id)
        if not room:
            raise NotFoundException("Phòng chơi không tồn tại")
        if room.status != GameRoomStatus.waiting:
            raise AppException("Phòng đã bắt đầu hoặc kết thúc", status_code=400)
        if room.white_player_id == player_id:
            raise AppException("Không thể tự chơi với chính mình", status_code=400)
        room.black_player_id = player_id
        room.status = GameRoomStatus.playing
        room = await self.repository.update_room(room)
        return GameRoomResponse.model_validate(room)

    async def make_move(
        self, room_id: uuid.UUID, notation: str, fen_after: str | None = None
    ) -> MoveHistoryResponse:
        room = await self.repository.get_room_by_id(room_id)
        if not room:
            raise NotFoundException("Phòng chơi không tồn tại")
        if room.status != GameRoomStatus.playing:
            raise AppException("Ván đấu chưa bắt đầu hoặc đã kết thúc", status_code=400)

        moves = await self.repository.get_moves(room_id)
        move_number = len(moves) + 1

        move = MoveHistory(room_id=room_id, move_number=move_number, notation=notation, fen_after=fen_after)
        move = await self.repository.add_move(move)

        if fen_after:
            room.fen = fen_after
            await self.repository.update_room(room)

        return MoveHistoryResponse.model_validate(move)

    async def end_game(self, room_id: uuid.UUID, result: str) -> GameRoomResponse:
        room = await self.repository.get_room_by_id(room_id)
        if not room:
            raise NotFoundException("Phòng chơi không tồn tại")
        room.status = GameRoomStatus.finished
        room.result = result
        room = await self.repository.update_room(room)
        return GameRoomResponse.model_validate(room)

    async def import_game(self, data: ImportGameRequest) -> GameRoomResponse:
        """Import ván đấu offline hoặc nhập kết quả thủ công."""
        from app.modules.games.rating_helper import calculate_rating_for_import

        room = GameRoom(
            white_player_id=data.white_player_id,
            black_player_id=data.black_player_id,
            game_type=data.game_type,
            time_control=0,
            status=GameRoomStatus.finished,
            result=data.result,
        )
        room = await self.repository.create_room(room)

        # Lưu moves nếu có
        for idx, notation in enumerate(data.moves, start=1):
            move = MoveHistory(room_id=room.id, move_number=idx, notation=notation)
            await self.repository.add_move(move)

        # Tính ELO nếu rated=True
        if data.rated:
            await calculate_rating_for_import(
                db=self.repository.db,
                white_player_id=data.white_player_id,
                black_player_id=data.black_player_id,
                game_type_str=data.game_type,
                result=data.result,
                room_id=room.id,
            )

        return GameRoomResponse.model_validate(room)

    async def get_moves(self, room_id: uuid.UUID) -> list[MoveHistoryResponse]:
        moves = await self.repository.get_moves(room_id)
        return [MoveHistoryResponse.model_validate(m) for m in moves]

    async def review_game(self, room_id: uuid.UUID) -> GameRoomResponse:
        """Chấm điểm ván đấu bằng engine (gọi Analysis service)."""
        import httpx

        from app.core.config import settings

        room = await self.repository.get_room_by_id(room_id)
        if not room:
            raise NotFoundException("Phòng chơi không tồn tại")
        if room.status != GameRoomStatus.finished:
            raise AppException("Ván đấu chưa kết thúc", status_code=400)
        if room.is_reviewed:
            return GameRoomResponse.model_validate(room)

        moves = await self.repository.get_moves(room_id)
        move_notations = [m.notation for m in moves]

        if not move_notations:
            raise AppException("Ván đấu không có nước đi", status_code=400)

        analysis_urls = {
            "chess": settings.ANALYSIS_CHESS_URL,
            "xiangqi": settings.ANALYSIS_XIANGQI_URL,
            "go": settings.ANALYSIS_GO_URL,
        }
        base_url = analysis_urls.get(room.game_type, settings.ANALYSIS_CHESS_URL)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/api/v1/analyze/game",
                json={"moves": move_notations, "depth": 18},
            )

        if response.status_code != 200:
            raise AppException("Không thể chấm điểm ván đấu", status_code=502)

        result = response.json()
        room.white_accuracy = result.get("accuracy_white", 0)
        room.black_accuracy = result.get("accuracy_black", 0)
        room.is_reviewed = True

        # Lưu classification + eval vào từng move
        move_classifications = result.get("moves", [])
        for i, mc in enumerate(move_classifications):
            if i < len(moves):
                moves[i].classification = mc.get("classification")
                moves[i].eval_after = int(mc.get("eval_after", 0))
                moves[i].best_move = mc.get("best_move")

        room = await self.repository.update_room(room)
        return GameRoomResponse.model_validate(room)

    async def get_finished_games(self, limit: int = 50) -> list[GameRoomResponse]:
        """Lấy danh sách ván đấu đã kết thúc (public)."""
        rooms = await self.repository.get_finished_rooms(limit)
        return [GameRoomResponse.model_validate(r) for r in rooms]

    async def export_pgn(self, room_id: uuid.UUID) -> str:
        """Export PGN — gọi analysis service để generate chuẩn format."""
        import httpx

        from app.core.config import settings

        room = await self.repository.get_room_by_id(room_id)
        if not room:
            raise NotFoundException("Phòng chơi không tồn tại")

        moves = await self.repository.get_moves(room_id)
        move_notations = [m.notation for m in moves]

        result_map = {"white_win": "1-0", "black_win": "0-1", "draw": "1/2-1/2"}

        # Gọi analysis service để generate PGN
        analysis_urls = {
            "chess": settings.ANALYSIS_CHESS_URL,
            "xiangqi": settings.ANALYSIS_XIANGQI_URL,
            "go": settings.ANALYSIS_GO_URL,
        }
        base_url = analysis_urls.get(room.game_type, settings.ANALYSIS_CHESS_URL)

        payload = {
            "moves": move_notations,
            "headers": {
                "Event": "VCC Platform",
                "Site": "Online",
                "Date": room.created_at.strftime("%Y.%m.%d") if room.created_at else "????.??.??",
                "White": str(room.white_player_id),
                "Black": str(room.black_player_id or "?"),
                "Result": result_map.get(room.result or "", "*"),
            },
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(f"{base_url}/api/v1/export/pgn", json=payload)

            if response.status_code == 200:
                return response.json().get("pgn", "")
        except Exception:
            pass

        # Fallback: raw text format nếu service không available
        lines = [
            f'[Event "VCC Platform"]',
            f'[White "{room.white_player_id}"]',
            f'[Black "{room.black_player_id or "?"}"]',
            f'[Result "{result_map.get(room.result or "", "*")}"]',
            "",
            " ".join(move_notations),
            result_map.get(room.result or "", "*"),
        ]
        return "\n".join(lines)

    async def create_room_from_match(self, match_id: uuid.UUID) -> GameRoomResponse:
        """Tạo phòng chơi online từ ván đấu trong giải đấu."""
        from sqlalchemy import select
        from app.modules.tournaments.models import Match, TournamentRound, Tournament

        # Lấy match info qua repository db session
        db = self.repository.db
        query = (
            select(Match)
            .where(Match.id == match_id, Match.is_deleted.is_(False))
        )
        result = await db.execute(query)
        match = result.scalar_one_or_none()
        if not match:
            raise NotFoundException("Ván đấu không tồn tại")

        # Lấy tournament info để biết game_type và time_control
        round_query = select(TournamentRound).where(TournamentRound.id == match.round_id)
        round_result = await db.execute(round_query)
        round_obj = round_result.scalar_one_or_none()

        tournament_query = select(Tournament).where(Tournament.id == round_obj.tournament_id)
        tournament_result = await db.execute(tournament_query)
        tournament = tournament_result.scalar_one_or_none()

        # Map time_format to seconds
        time_map = {"bullet": 60, "blitz": 300, "rapid": 600, "standard": 1800}
        time_control = time_map.get(tournament.time_format.value, 300)

        room = GameRoom(
            match_id=match_id,
            white_player_id=match.white_player_id,
            black_player_id=match.black_player_id,
            game_type=tournament.game_type.value,
            time_control=time_control,
            increment=0,
            scheduled_start=round_obj.start_time,  # None cho OTB, datetime cho online
            status=GameRoomStatus.waiting,  # waiting until scheduled_start
        )
        room = await self.repository.create_room(room)
        return GameRoomResponse.model_validate(room)
