"""In-memory matchmaking queue for finding opponents."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class QueueEntry:
    member_id: uuid.UUID
    rating: int
    game_type: str
    time_format: str
    joined_at: datetime = field(default_factory=datetime.utcnow)


# In-memory queue: key = (game_type, time_format), value = list of entries
_matchmaking_queue: dict[tuple[str, str], list[QueueEntry]] = {}


def add_to_queue(
    member_id: uuid.UUID, rating: int, game_type: str, time_format: str
) -> QueueEntry:
    """Thêm người chơi vào hàng đợi tìm trận."""
    key = (game_type, time_format)
    if key not in _matchmaking_queue:
        _matchmaking_queue[key] = []

    # Xóa entry cũ nếu đã tồn tại
    _matchmaking_queue[key] = [
        e for e in _matchmaking_queue[key] if e.member_id != member_id
    ]

    entry = QueueEntry(
        member_id=member_id, rating=rating,
        game_type=game_type, time_format=time_format,
    )
    _matchmaking_queue[key].append(entry)
    return entry


def remove_from_queue(member_id: uuid.UUID, game_type: str, time_format: str) -> bool:
    """Xóa người chơi khỏi hàng đợi."""
    key = (game_type, time_format)
    if key not in _matchmaking_queue:
        return False
    before = len(_matchmaking_queue[key])
    _matchmaking_queue[key] = [
        e for e in _matchmaking_queue[key] if e.member_id != member_id
    ]
    return len(_matchmaking_queue[key]) < before


def find_match(
    member_id: uuid.UUID, rating: int, game_type: str,
    time_format: str, rating_range: int = 200,
) -> QueueEntry | None:
    """Tìm đối thủ trong khoảng ±rating_range."""
    key = (game_type, time_format)
    if key not in _matchmaking_queue:
        return None

    for entry in _matchmaking_queue[key]:
        if entry.member_id == member_id:
            continue
        if abs(entry.rating - rating) <= rating_range:
            # Xóa cả hai khỏi queue
            _matchmaking_queue[key] = [
                e for e in _matchmaking_queue[key]
                if e.member_id not in (member_id, entry.member_id)
            ]
            return entry
    return None


def is_in_queue(member_id: uuid.UUID) -> tuple[str, str] | None:
    """Kiểm tra người chơi có đang trong queue không."""
    for (game_type, time_format), entries in _matchmaking_queue.items():
        for entry in entries:
            if entry.member_id == member_id:
                return (game_type, time_format)
    return None
