import uuid

from app.core.exceptions import AppException, NotFoundException
from app.modules.tournaments.models import (
    GameType,
    Match,
    Tournament,
    TournamentParticipant,
    TournamentRound,
    TournamentStatus,
)
from app.modules.tournaments.repository import TournamentRepository
from app.modules.tournaments.schemas import (
    MatchResponse,
    MatchResultUpdate,
    ParticipantCreate,
    ParticipantResponse,
    RoundCreate,
    RoundResponse,
    TournamentCreate,
    TournamentPrize,
    TournamentPrizeResponse,
    TournamentResponse,
    TournamentUpdate,
)


class TournamentService:
    def __init__(self, repository: TournamentRepository):
        self.repository = repository

    async def list_tournaments(
        self,
        page: int,
        page_size: int,
        status: TournamentStatus | None = None,
        game_type: GameType | None = None,
    ) -> tuple[list[TournamentResponse], int]:
        tournaments, total = await self.repository.get_all(page, page_size, status, game_type)
        return [TournamentResponse.model_validate(t) for t in tournaments], total

    async def get_tournament(self, tournament_id: uuid.UUID) -> TournamentResponse:
        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")
        return TournamentResponse.model_validate(tournament)

    async def create_tournament(self, data: TournamentCreate) -> TournamentResponse:
        tournament = Tournament(**data.model_dump())
        tournament = await self.repository.create(tournament)
        return TournamentResponse.model_validate(tournament)

    async def update_tournament(self, tournament_id: uuid.UUID, data: TournamentUpdate) -> TournamentResponse:
        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(tournament, field, value)
        tournament = await self.repository.update(tournament)
        return TournamentResponse.model_validate(tournament)

    async def delete_tournament(self, tournament_id: uuid.UUID) -> None:
        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")
        await self.repository.soft_delete(tournament)

    # --- Participants ---

    async def add_participant(
        self, tournament_id: uuid.UUID, data: ParticipantCreate
    ) -> ParticipantResponse:
        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")
        participant = TournamentParticipant(tournament_id=tournament_id, member_id=data.member_id)
        participant = await self.repository.add_participant(participant)
        return ParticipantResponse.model_validate(participant)

    async def list_participants(self, tournament_id: uuid.UUID) -> list[ParticipantResponse]:
        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")
        participants = await self.repository.get_participants(tournament_id)
        return [ParticipantResponse.model_validate(p) for p in participants]

    # --- Rounds ---

    async def create_round(self, tournament_id: uuid.UUID, data: RoundCreate) -> RoundResponse:
        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")
        round_ = TournamentRound(tournament_id=tournament_id, round_number=data.round_number, start_time=data.start_time)
        round_ = await self.repository.create_round(round_)
        return RoundResponse.model_validate(round_)

    async def list_rounds(self, tournament_id: uuid.UUID) -> list[RoundResponse]:
        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")
        rounds = await self.repository.get_rounds(tournament_id)
        return [RoundResponse.model_validate(r) for r in rounds]

    async def create_rooms_for_round(self, tournament_id: uuid.UUID, round_id: uuid.UUID) -> int:
        """Tạo game rooms cho tất cả matches pending trong round (online tournament)."""
        from app.modules.games.models import GameRoom, GameRoomStatus

        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")

        rounds = await self.repository.get_rounds(tournament_id)
        round_obj = next((r for r in rounds if r.id == round_id), None)
        if not round_obj:
            raise NotFoundException("Vòng đấu không tồn tại")

        time_map = {"bullet": 60, "blitz": 300, "rapid": 600, "standard": 1800}
        time_control = time_map.get(tournament.time_format.value, 300)
        count = 0

        for match in round_obj.matches:
            if match.result.value != "pending":
                continue
            room = GameRoom(
                match_id=match.id,
                white_player_id=match.white_player_id,
                black_player_id=match.black_player_id,
                game_type=tournament.game_type.value,
                time_control=time_control,
                increment=0,
                scheduled_start=round_obj.start_time,
                status=GameRoomStatus.waiting,
            )
            self.repository.db.add(room)
            count += 1

        await self.repository.db.commit()
        return count

    # --- Pairings ---

    async def generate_pairings(self, tournament_id: uuid.UUID) -> list[RoundResponse]:
        from app.modules.tournaments.pairing import (
            generate_knockout_pairings,
            generate_round_robin_pairings,
            generate_swiss_pairings,
        )

        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")

        participants = await self.repository.get_participants(tournament_id)
        player_ids = [p.member_id for p in participants if p.status.value != "withdrawn"]

        if len(player_ids) < 2:
            raise AppException("Cần ít nhất 2 người chơi để tạo cặp đấu", status_code=400)

        if tournament.format.value == "round_robin":
            all_rounds = generate_round_robin_pairings(player_ids)
            for round_num, pairings in enumerate(all_rounds, start=1):
                round_ = TournamentRound(tournament_id=tournament_id, round_number=round_num)
                round_ = await self.repository.create_round(round_)
                for white_id, black_id in pairings:
                    match = Match(round_id=round_.id, white_player_id=white_id, black_player_id=black_id)
                    await self.repository.create_match(match)
        elif tournament.format.value == "knockout":
            pairings = generate_knockout_pairings(player_ids)
            round_ = TournamentRound(tournament_id=tournament_id, round_number=1)
            round_ = await self.repository.create_round(round_)
            for white_id, black_id in pairings:
                match = Match(round_id=round_.id, white_player_id=white_id, black_player_id=black_id)
                await self.repository.create_match(match)
        else:
            # Swiss: sử dụng thuật toán Swiss pairing
            previous_matches = await self.repository.get_all_matches(tournament_id)
            existing_rounds = await self.repository.get_rounds(tournament_id)
            next_round_num = len(existing_rounds) + 1
            pairings = generate_swiss_pairings(player_ids, previous_matches)
            round_ = TournamentRound(tournament_id=tournament_id, round_number=next_round_num)
            round_ = await self.repository.create_round(round_)
            for white_id, black_id in pairings:
                match = Match(round_id=round_.id, white_player_id=white_id, black_player_id=black_id)
                await self.repository.create_match(match)

        await self.repository.commit()

        # Cập nhật trạng thái giải đấu
        tournament.status = TournamentStatus.in_progress
        await self.repository.commit()

        rounds = await self.repository.get_rounds(tournament_id)
        return [RoundResponse.model_validate(r) for r in rounds]

    # --- Matches ---

    async def update_match_result(self, match_id: uuid.UUID, data: MatchResultUpdate) -> MatchResponse:
        match = await self.repository.get_match_by_id(match_id)
        if not match:
            raise NotFoundException("Ván đấu không tồn tại")
        match.result = data.result
        if data.played_at:
            match.played_at = data.played_at
        match = await self.repository.update_match(match)
        return MatchResponse.model_validate(match)

    # --- Standings ---

    async def get_standings(self, tournament_id: uuid.UUID) -> list["StandingsEntry"]:
        from app.modules.tournaments.schemas import StandingsEntry
        from app.modules.tournaments.standings import calculate_standings

        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")

        participants = await self.repository.get_participants(tournament_id)
        participant_ids = [p.member_id for p in participants if p.status.value != "withdrawn"]

        matches = await self.repository.get_all_matches(tournament_id)
        standings_data = calculate_standings(matches, participant_ids)

        return [
            StandingsEntry(
                rank=s.rank,
                member_id=s.member_id,
                points=s.points,
                wins=s.wins,
                draws=s.draws,
                losses=s.losses,
                buchholz=s.buchholz,
                sonneborn_berger=s.sonneborn_berger,
            )
            for s in standings_data
        ]

    # --- Prizes ---

    async def get_prizes(self, tournament_id: uuid.UUID) -> TournamentPrizeResponse:
        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")
        prizes_data = tournament.prizes_json or []
        prizes = [TournamentPrize(**p) for p in prizes_data]
        return TournamentPrizeResponse(tournament_id=tournament_id, prizes=prizes)

    async def set_prizes(
        self, tournament_id: uuid.UUID, prizes: list[TournamentPrize]
    ) -> TournamentPrizeResponse:
        tournament = await self.repository.get_by_id(tournament_id)
        if not tournament:
            raise NotFoundException("Giải đấu không tồn tại")
        tournament.prizes_json = [p.model_dump(mode="json") for p in prizes]
        await self.repository.commit()
        return TournamentPrizeResponse(tournament_id=tournament_id, prizes=prizes)
