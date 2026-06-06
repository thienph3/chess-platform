"""Redis pub/sub for multi-pod WebSocket broadcasting.

Each pod subscribes to game channels. When a move/event happens,
it's published to Redis and all pods relay to their local WebSocket clients.
"""
import asyncio
import json
import logging
from typing import Callable, Awaitable

from app.modules.games.redis_store import get_redis

logger = logging.getLogger(__name__)

_subscribers: dict[str, list[Callable[[dict], Awaitable[None]]]] = {}
_listener_task: asyncio.Task | None = None
_pubsub = None


def _channel(room_key: str) -> str:
    return f"chess:pubsub:{room_key}"


async def publish(room_key: str, message: dict) -> None:
    """Publish a message to all pods listening to this room."""
    r = get_redis()
    try:
        await r.publish(_channel(room_key), json.dumps(message))
    except Exception as exc:
        logger.warning("Pub/sub publish failed: %s", exc)


async def subscribe(room_key: str, callback: Callable[[dict], Awaitable[None]]) -> None:
    """Subscribe this pod to a room's messages."""
    global _listener_task, _pubsub

    if room_key not in _subscribers:
        _subscribers[room_key] = []

        # Subscribe to Redis channel
        r = get_redis()
        if _pubsub is None:
            _pubsub = r.pubsub()

        try:
            await _pubsub.subscribe(_channel(room_key))
        except Exception as exc:
            logger.warning("Pub/sub subscribe failed: %s", exc)

    _subscribers[room_key].append(callback)

    # Start listener if not running
    if _listener_task is None or _listener_task.done():
        _listener_task = asyncio.create_task(_listen_loop())


async def unsubscribe(room_key: str, callback: Callable[[dict], Awaitable[None]]) -> None:
    """Remove a callback. Unsubscribe from channel if no more listeners."""
    if room_key in _subscribers:
        _subscribers[room_key] = [cb for cb in _subscribers[room_key] if cb != callback]
        if not _subscribers[room_key]:
            del _subscribers[room_key]
            if _pubsub:
                try:
                    await _pubsub.unsubscribe(_channel(room_key))
                except Exception:
                    pass


async def _listen_loop() -> None:
    """Background loop reading messages from all subscribed channels."""
    while _pubsub and _subscribers:
        try:
            message = await _pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message["type"] == "message":
                channel = message["channel"]
                # Extract room_key from channel name
                room_key = channel.replace("chess:pubsub:", "") if isinstance(channel, str) else channel.decode().replace("chess:pubsub:", "")
                data = json.loads(message["data"])

                # Dispatch to local callbacks
                for cb in _subscribers.get(room_key, []):
                    try:
                        await cb(data)
                    except Exception as exc:
                        logger.warning("Pub/sub callback error: %s", exc)
        except asyncio.CancelledError:
            return
        except Exception as exc:
            logger.warning("Pub/sub listener error: %s", exc)
            await asyncio.sleep(1)
