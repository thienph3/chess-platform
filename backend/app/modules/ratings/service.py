import uuid

from app.core.exceptions import AppException, NotFoundException
from app.modules.ratings.elo import INITIAL_RATING, calculate_new_rating
from app.modules.ratings.models import Rating, RatingChange
from app.modules.ratings.repository import RatingRepository
from app.modules.ratings.schemas import (
    CalculateResponse,
    LeaderboardEntry,
    RatingChangeResponse,
    RatingResponse,
)
from app.modules.tournaments.models import GameType, MatchResult, TimeFormat


class RatingService:
    def __init__(self, repository: RatingRepository):
        self.repository = repository

    async def get_leaderboard(
        self, game_type: GameType, time_format: TimeFormat, limit: int = 20
    ) -> list[LeaderboardEntry]:
        ratings = await self.repository.get_leaderboard(game_type, time_format, limit)
        return [LeaderboardEntry.model_validate(r) for r in ratings]

    async def get_member_ratings(self, member_id: uuid.UUID) -> list[RatingResponse]:
        ratings = await self.repository.get_ratings_by_member(member_id)
        return [RatingResponse.model_validate(r) for r in ratings]

    async def get_rating_history(
        self, member_id: uuid.UUID, game_type: GameType, time_format: TimeFormat
    ) -> list[RatingChangeResponse]:
        changes = await self.repository.get_history(member_id, game_type, time_format)
        return [RatingChangeResponse.model_validate(c) for c in changes]

    async def calculate_match_rating(self, match_id: uuid.UUID) -> CalculateResponse:
        match = await self.repository.get_match_by_id(match_id)
        if not match:
            raise NotFoundException("Ván đấu không tồn tại")
        if match.result == MatchResult.pending:
            raise AppException("Ván đấu chưa có kết quả", status_code=400)

        # Lấy thông tin giải đấu để xác định game_type và time_format
        round_obj = match.round
        tournament = round_obj.tournament
        game_type = tournament.game_type
        time_format = tournament.time_format

        # Lấy hoặc tạo rating cho cả hai người chơi
        white_rating = await self._get_or_create_rating(
            match.white_player_id, game_type, time_format
        )
        black_rating = await self._get_or_create_rating(
            match.black_player_id, game_type, time_format
        )

        # Xác định actual score
        white_score, black_score = self._get_scores(match.result)

        # Tính ELO mới
        white_old = white_rating.rating
        black_old = black_rating.rating
        white_new = calculate_new_rating(
            white_old, black_old, white_score, white_rating.games_played
        )
        black_new = calculate_new_rating(
            black_old, white_old, black_score, black_rating.games_played
        )

        # Lưu rating changes và cập nhật ratings
        await self._save_rating_change(white_rating, match.id, white_new)
        await self._save_rating_change(black_rating, match.id, black_new)
        self._update_stats(white_rating, white_new, match.result, is_white=True)
        self._update_stats(black_rating, black_new, match.result, is_white=False)

        await self.repository.commit()

        return CalculateResponse(
            white_player_id=match.white_player_id,
            black_player_id=match.black_player_id,
            white_old_rating=white_old,
            white_new_rating=white_new,
            black_old_rating=black_old,
            black_new_rating=black_new,
        )

    async def _get_or_create_rating(
        self, member_id: uuid.UUID, game_type: GameType, time_format: TimeFormat
    ) -> Rating:
        rating = await self.repository.get_rating(member_id, game_type, time_format)
        if not rating:
            rating = Rating(
                member_id=member_id,
                game_type=game_type,
                time_format=time_format,
                rating=INITIAL_RATING,
                games_played=0,
                wins=0,
                draws=0,
                losses=0,
            )
            rating = await self.repository.create_rating(rating)
        return rating

    async def _save_rating_change(
        self, rating: Rating, match_id: uuid.UUID, new_rating: int
    ) -> None:
        change = RatingChange(
            rating_id=rating.id,
            match_id=match_id,
            old_rating=rating.rating,
            new_rating=new_rating,
            change=new_rating - rating.rating,
        )
        await self.repository.create_rating_change(change)

    def _get_scores(self, result: MatchResult) -> tuple[float, float]:
        if result == MatchResult.white_win:
            return 1.0, 0.0
        elif result == MatchResult.black_win:
            return 0.0, 1.0
        return 0.5, 0.5

    def _update_stats(
        self, rating: Rating, new_rating: int, result: MatchResult, is_white: bool
    ) -> None:
        rating.rating = new_rating
        rating.games_played += 1
        if result == MatchResult.draw:
            rating.draws += 1
        elif (result == MatchResult.white_win and is_white) or (
            result == MatchResult.black_win and not is_white
        ):
            rating.wins += 1
        else:
            rating.losses += 1
