"""Challenge endpoints — thách đấu trực tiếp."""
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppException, NotFoundException
from app.db.session import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.schemas import UserResponse
from app.modules.games.challenge_schemas import ChallengeCreate, ChallengeResponse
from app.modules.games.models import Challenge, ChallengeStatus, GameRoom, GameRoomStatus
from app.shared.schemas import ResponseEnvelope

router = APIRouter(prefix="/games/challenges", tags=["Challenges"])


@router.post("", response_model=ResponseEnvelope[ChallengeResponse], status_code=status.HTTP_201_CREATED)
async def create_challenge(
    data: ChallengeCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Tạo lời thách đấu."""
    if current_user.member_id == data.challenged_id:
        raise AppException("Không thể thách đấu chính mình", status_code=400)

    challenge = Challenge(
        challenger_id=current_user.member_id,
        challenged_id=data.challenged_id,
        game_type=data.game_type,
        time_control=data.time_control,
        status=ChallengeStatus.pending,
    )
    db.add(challenge)
    await db.commit()
    await db.refresh(challenge)
    return ResponseEnvelope(data=ChallengeResponse.model_validate(challenge), message="Đã gửi thách đấu")


@router.get("/pending", response_model=ResponseEnvelope[list[ChallengeResponse]])
async def get_pending_challenges(
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Lấy danh sách thách đấu đang chờ (gửi đến mình)."""
    query = (
        select(Challenge)
        .where(
            Challenge.challenged_id == current_user.member_id,
            Challenge.status == ChallengeStatus.pending,
            Challenge.is_deleted.is_(False),
        )
        .order_by(Challenge.created_at.desc())
    )
    result = await db.execute(query)
    challenges = list(result.scalars().all())
    return ResponseEnvelope(data=[ChallengeResponse.model_validate(c) for c in challenges])


@router.post("/{challenge_id}/accept", response_model=ResponseEnvelope[ChallengeResponse])
async def accept_challenge(
    challenge_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chấp nhận thách đấu → tạo phòng chơi."""
    challenge = await _get_challenge(db, challenge_id)
    if challenge.challenged_id != current_user.member_id:
        raise AppException("Bạn không phải người được thách đấu", status_code=403)
    if challenge.status != ChallengeStatus.pending:
        raise AppException("Thách đấu không còn hiệu lực", status_code=400)

    challenge.status = ChallengeStatus.accepted
    # Tạo phòng chơi
    room = GameRoom(
        white_player_id=challenge.challenger_id,
        black_player_id=challenge.challenged_id,
        game_type=challenge.game_type,
        time_control=challenge.time_control,
        status=GameRoomStatus.playing,
    )
    db.add(room)
    await db.commit()
    await db.refresh(challenge)
    return ResponseEnvelope(data=ChallengeResponse.model_validate(challenge), message="Đã chấp nhận thách đấu")


@router.post("/{challenge_id}/decline", response_model=ResponseEnvelope[ChallengeResponse])
async def decline_challenge(
    challenge_id: uuid.UUID,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Từ chối thách đấu."""
    challenge = await _get_challenge(db, challenge_id)
    if challenge.challenged_id != current_user.member_id:
        raise AppException("Bạn không phải người được thách đấu", status_code=403)
    if challenge.status != ChallengeStatus.pending:
        raise AppException("Thách đấu không còn hiệu lực", status_code=400)

    challenge.status = ChallengeStatus.declined
    await db.commit()
    await db.refresh(challenge)
    return ResponseEnvelope(data=ChallengeResponse.model_validate(challenge), message="Đã từ chối thách đấu")


async def _get_challenge(db: AsyncSession, challenge_id: uuid.UUID) -> Challenge:
    query = select(Challenge).where(Challenge.id == challenge_id, Challenge.is_deleted.is_(False))
    result = await db.execute(query)
    challenge = result.scalar_one_or_none()
    if not challenge:
        raise NotFoundException("Thách đấu không tồn tại")
    return challenge
