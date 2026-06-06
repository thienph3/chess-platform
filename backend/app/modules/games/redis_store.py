"""Redis-backed game state store.

Stores game clocks, FEN, turn, ready status — survives pod restarts.
Key format: chess:room:{room_id}:{field}
"""
import json
import logging
import os
import time
from typing import Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME", "default")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_SSL = os.getenv("REDIS_SSL", "false") == "true"

_pool: redis.Redis | None = None
_available: bool | None = None  # Cache availability check


def _is_configured() -> bool:
    """Return False if Redis is not configured (skip all operations)."""
    return bool(REDIS_HOST) and REDIS_HOST != "localhost" or REDIS_PASSWORD != ""


def get_redis() -> redis.Redis:
    global _pool
    if _pool is None:
        _pool = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            username=REDIS_USERNAME if REDIS_USERNAME != "default" else None,
            password=REDIS_PASSWORD or None,
            ssl=REDIS_SSL,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
    return _pool


async def _check_available() -> bool:
    global _available
    if _available is not None:
        return _available
    if not _is_configured():
        _available = False
        return False
    try:
        r = get_redis()
        await r.ping()
        _available = True
    except Exception:
        _available = False
    return _available


def _key(room_id: str, field: str) -> str:
    return f"chess:room:{room_id}:{field}"


async def save_game_state(room_id: str, state: dict[str, Any]) -> None:
    """Save full game state to Redis (TTL 3 hours)."""
    if not await _check_available():
        return
    r = get_redis()
    try:
        await r.set(_key(room_id, "state"), json.dumps(state), ex=10800)
    except Exception as exc:
        logger.warning("Redis save failed: %s", exc)


async def get_game_state(room_id: str) -> dict[str, Any] | None:
    """Load game state from Redis."""
    if not await _check_available():
        return None
    r = get_redis()
    try:
        data = await r.get(_key(room_id, "state"))
        return json.loads(data) if data else None
    except Exception as exc:
        logger.warning("Redis get failed: %s", exc)
        return None


async def save_clock(room_id: str, white_ms: int, black_ms: int, active: str, last_move_time: float, increment_ms: int, started: bool) -> None:
    """Save clock state."""
    if not await _check_available():
        return
    r = get_redis()
    clock = {
        "white_ms": white_ms,
        "black_ms": black_ms,
        "active": active,
        "last_move_time": last_move_time,
        "increment_ms": increment_ms,
        "started": started,
    }
    try:
        await r.set(_key(room_id, "clock"), json.dumps(clock), ex=10800)
    except Exception as exc:
        logger.warning("Redis clock save failed: %s", exc)


async def get_clock(room_id: str) -> dict[str, Any] | None:
    """Load clock state."""
    if not await _check_available():
        return None
    r = get_redis()
    try:
        data = await r.get(_key(room_id, "clock"))
        return json.loads(data) if data else None
    except Exception as exc:
        logger.warning("Redis clock get failed: %s", exc)
        return None


async def set_ready(room_id: str, player_index: int) -> int:
    """Mark player as ready. Returns total ready count."""
    if not await _check_available():
        return 0
    r = get_redis()
    try:
        key = _key(room_id, "ready")
        await r.sadd(key, str(player_index))
        await r.expire(key, 600)
        return await r.scard(key)
    except Exception as exc:
        logger.warning("Redis ready failed: %s", exc)
        return 0


async def clear_ready(room_id: str) -> None:
    if not await _check_available():
        return
    r = get_redis()
    try:
        await r.delete(_key(room_id, "ready"))
    except Exception as exc:
        logger.warning("Redis clear ready failed: %s", exc)


async def delete_room(room_id: str) -> None:
    """Clean up all Redis keys for a room."""
    if not await _check_available():
        return
    r = get_redis()
    try:
        await r.delete(_key(room_id, "state"), _key(room_id, "clock"), _key(room_id, "ready"))
    except Exception as exc:
        logger.warning("Redis delete failed: %s", exc)


async def is_available() -> bool:
    """Check Redis connectivity."""
    try:
        r = get_redis()
        await r.ping()
        return True
    except Exception:
        return False
