"""AI Bot Worker — plays as a bot through the same WebSocket game flow.

When an AI game room is created, the bot:
1. Joins the room (already assigned as player in DB)
2. Auto-readies
3. On its turn, calls analysis service for best move
4. Sends move through WebSocket

This makes AI games identical to Human vs Human from the protocol perspective.
"""
import asyncio
import json
import logging
import uuid

import httpx

from app.core.config import settings
from app.modules.games.validation_client import ANALYSIS_URLS

logger = logging.getLogger(__name__)

AI_PLAYER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DIFFICULTY_DEPTH = {"easy": 3, "medium": 10, "hard": 18}

# Track active bot tasks
_bot_tasks: dict[str, asyncio.Task] = {}


async def start_bot_for_room(room_id: uuid.UUID, game_type: str, difficulty: str = "medium") -> None:
    """Start an AI bot worker for a game room."""
    room_key = str(room_id)
    if room_key in _bot_tasks and not _bot_tasks[room_key].done():
        return  # Already running

    task = asyncio.create_task(_bot_loop(room_id, game_type, difficulty))
    _bot_tasks[room_key] = task


async def _bot_loop(room_id: uuid.UUID, game_type: str, difficulty: str) -> None:
    """Main bot loop: connect to WebSocket, ready, play moves on its turn."""
    from app.modules.games.websocket import (
        room_connections, room_states, room_clocks, room_ready,
        PlayerConnection, _handle_ready, _handle_move, _get_active_color,
        _send, _broadcast,
    )

    room_key = str(room_id)
    bot_player_id = str(AI_PLAYER_ID)

    # Determine bot's role
    from app.db.session import async_session_factory
    from app.modules.games.repository import GameRepository
    try:
        async with async_session_factory() as db:
            repo = GameRepository(db)
            room = await repo.get_room_by_id(room_id)
            if not room:
                return
            if str(room.white_player_id) == bot_player_id:
                bot_role = "white"
            elif room.black_player_id and str(room.black_player_id) == bot_player_id:
                bot_role = "black"
            else:
                return
    except Exception as exc:
        logger.error("Bot init failed: %s", exc)
        return

    # Create a fake connection (no real WebSocket — bot acts internally)
    class BotWebSocket:
        """Fake WebSocket that discards outgoing messages."""
        async def send_text(self, data: str) -> None:
            pass  # Bot doesn't need to receive messages — it reacts to state

    bot_ws = BotWebSocket()
    conn = PlayerConnection(bot_ws, bot_player_id, bot_role)  # type: ignore
    room_connections[room_key].append(conn)

    # Wait for room state to be initialized
    for _ in range(30):
        if room_key in room_states:
            break
        await asyncio.sleep(0.5)
    else:
        room_connections[room_key].remove(conn)
        return

    # Auto-ready after a short delay (feels more natural)
    await asyncio.sleep(1)
    room_ready[room_key].add(bot_player_id)
    await _broadcast(room_key, {"type": "ready_status", "ready_count": len(room_ready[room_key]), "needed": 2})

    # If both ready, _handle_ready will be triggered by the human's ready
    # But if bot readied second, we need to trigger countdown
    if len(room_ready[room_key]) >= 2:
        await _handle_ready(room_key, conn, room_id)

    # Game loop: wait for our turn, make a move
    while True:
        await asyncio.sleep(0.5)

        state = room_states.get(room_key)
        if not state:
            break
        if state.get("game_over"):
            break
        if not state.get("started"):
            continue

        # Check if it's bot's turn
        active_color = _get_active_color(room_key)
        if active_color != bot_role:
            continue

        # Think (slight delay for natural feel)
        await asyncio.sleep(0.8)

        # Get best move from analysis service
        fen = state.get("fen", "")
        move = await _get_ai_move(fen, game_type, difficulty)
        if not move:
            # Engine unavailable — resign
            logger.warning("Bot engine unavailable, resigning room %s", room_key)
            break

        # Parse and play move
        move_dict = _parse_move(game_type, move)
        await _handle_move(room_key, move_dict, conn, room_id)

    # Cleanup
    if conn in room_connections.get(room_key, []):
        room_connections[room_key].remove(conn)
    _bot_tasks.pop(room_key, None)


async def _get_ai_move(fen: str, game_type: str, difficulty: str) -> str | None:
    """Call analysis service for best move."""
    base_url = ANALYSIS_URLS.get(game_type)
    if not base_url:
        return None
    depth = DIFFICULTY_DEPTH.get(difficulty, 10)
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{base_url}/api/v1/analyze/suggest", json={"fen": fen, "depth": depth})
        if resp.status_code == 200:
            return resp.json().get("best_move")
    except Exception as exc:
        logger.error("Bot AI move error: %s", exc)
    return None


def _parse_move(game_type: str, move_str: str) -> dict:
    """Parse engine move string to WebSocket move dict."""
    if game_type in ("gomoku", "go") and "," in move_str:
        parts = move_str.split(",")
        return {"row": int(parts[0]), "col": int(parts[1])}
    return {"from": move_str[:2], "to": move_str[2:4]}
