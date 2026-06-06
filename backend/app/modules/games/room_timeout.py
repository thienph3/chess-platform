"""Background task to expire stale game rooms.

- Waiting rooms: expire after 30 minutes (no opponent joined)
- Playing rooms: expire after 2 hours (abandoned game)
"""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update

from app.db.session import async_session_factory
from app.modules.games.models import GameRoom, GameRoomStatus

logger = logging.getLogger(__name__)

WAITING_TIMEOUT = timedelta(minutes=30)
PLAYING_TIMEOUT = timedelta(hours=2)
CHECK_INTERVAL = 60  # seconds


async def cleanup_stale_rooms() -> int:
    """Expire stale rooms. Returns number of rooms cleaned."""
    now = datetime.now(timezone.utc)
    count = 0

    async with async_session_factory() as db:
        # Waiting rooms older than 30 min → aborted
        waiting_cutoff = now - WAITING_TIMEOUT
        result = await db.execute(
            update(GameRoom)
            .where(GameRoom.status == GameRoomStatus.waiting)
            .where(GameRoom.created_at < waiting_cutoff)
            .values(status=GameRoomStatus.aborted)
        )
        count += result.rowcount

        # Playing rooms older than 2 hours → finished (draw by abandonment)
        playing_cutoff = now - PLAYING_TIMEOUT
        result = await db.execute(
            update(GameRoom)
            .where(GameRoom.status == GameRoomStatus.playing)
            .where(GameRoom.created_at < playing_cutoff)
            .values(status=GameRoomStatus.finished, result="draw")
        )
        count += result.rowcount

        await db.commit()

    if count > 0:
        logger.info("Cleaned up %d stale rooms", count)
    return count


async def room_cleanup_loop():
    """Run cleanup every 60 seconds."""
    while True:
        try:
            await cleanup_stale_rooms()
        except Exception as exc:
            logger.error("Room cleanup error: %s", exc)
        await asyncio.sleep(CHECK_INTERVAL)
