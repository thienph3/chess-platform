"""Helper để tính ELO cho ván đấu import."""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ratings.elo import INITIAL_RATING, calculate_new_rating
from app.modules.ratings.models import Rating, RatingChange
from app.modules.tournaments.models import GameType, TimeFormat


async def calculate_rating_for_import(
    db: AsyncSession,
    white_player_id: uuid.UUID,
    black_player_id: uuid.UUID,
    game_type_str: str,
    result: str,
    room_id: uuid.UUID,
) -> None:
    """Tính và cập nhật ELO cho ván import."""
    game_type = GameType(game_type_str)
    time_format = TimeFormat.rapid  # Import game mặc định dùng rapid

    white_rating = await _get_or_create_rating(db, white_player_id, game_type, time_format)
    black_rating = await _get_or_create_rating(db, black_player_id, game_type, time_format)

    # Xác định actual score
    if result == "white_win":
        w_score, b_score = 1.0, 0.0
    elif result == "black_win":
        w_score, b_score = 0.0, 1.0
    else:
        w_score, b_score = 0.5, 0.5

    w_new = calculate_new_rating(
        white_rating.rating, black_rating.rating, w_score, white_rating.games_played
    )
    b_new = calculate_new_rating(
        black_rating.rating, white_rating.rating, b_score, black_rating.games_played
    )

    # Lưu rating changes
    db.add(RatingChange(
        rating_id=white_rating.id, match_id=room_id,
        old_rating=white_rating.rating, new_rating=w_new, change=w_new - white_rating.rating,
    ))
    db.add(RatingChange(
        rating_id=black_rating.id, match_id=room_id,
        old_rating=black_rating.rating, new_rating=b_new, change=b_new - black_rating.rating,
    ))

    # Cập nhật stats
    white_rating.rating = w_new
    white_rating.games_played += 1
    black_rating.rating = b_new
    black_rating.games_played += 1

    if result == "white_win":
        white_rating.wins += 1
        black_rating.losses += 1
    elif result == "black_win":
        black_rating.wins += 1
        white_rating.losses += 1
    else:
        white_rating.draws += 1
        black_rating.draws += 1

    await db.commit()


async def _get_or_create_rating(
    db: AsyncSession, member_id: uuid.UUID, game_type: GameType, time_format: TimeFormat
) -> Rating:
    """Lấy hoặc tạo rating record cho member."""
    query = select(Rating).where(
        Rating.member_id == member_id,
        Rating.game_type == game_type,
        Rating.time_format == time_format,
        Rating.is_deleted.is_(False),
    )
    result = await db.execute(query)
    rating = result.scalar_one_or_none()
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
        db.add(rating)
        await db.flush()
    return rating
