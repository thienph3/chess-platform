"""WebSocket handler for real-time gameplay.

Flow: join → ready → countdown → playing (server clock) → finished
Auth: token passed as query param, maps WebSocket to player_id.
Turn enforcement: only active player can send moves.
Spectators: can watch but cannot send moves/resign/ready.
"""
import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.modules.games.validation_client import get_initial_state, validate_move
from app.modules.games import redis_store

logger = logging.getLogger(__name__)

ws_router = APIRouter()


# --- In-memory connection tracking ---

class PlayerConnection:
    def __init__(self, ws: WebSocket, player_id: str | None, role: str):
        self.ws = ws
        self.player_id = player_id  # member UUID or None for spectator
        self.role = role  # "white", "black", "spectator"


room_connections: dict[str, list[PlayerConnection]] = defaultdict(list)
room_states: dict[str, dict[str, Any]] = {}
room_ready: dict[str, set[str]] = defaultdict(set)  # set of player_ids
room_clocks: dict[str, dict[str, Any]] = {}


# --- Helpers ---

async def _broadcast(room_key: str, message: dict) -> None:
    msg = json.dumps(message)
    for conn in room_connections[room_key]:
        try:
            await conn.ws.send_text(msg)
        except Exception:
            pass


async def _send_to_players(room_key: str, message: dict) -> None:
    """Send only to white/black, not spectators."""
    msg = json.dumps(message)
    for conn in room_connections[room_key]:
        if conn.role in ("white", "black"):
            try:
                await conn.ws.send_text(msg)
            except Exception:
                pass


async def _send(ws: WebSocket, message: dict) -> None:
    try:
        await ws.send_text(json.dumps(message))
    except Exception:
        pass


def _get_connection(room_key: str, ws: WebSocket) -> PlayerConnection | None:
    for conn in room_connections[room_key]:
        if conn.ws == ws:
            return conn
    return None


def _get_clocks(room_key: str) -> dict[str, int]:
    clock = room_clocks.get(room_key)
    if not clock or not clock.get("started"):
        return {"white_clock": clock["white_ms"] if clock else 0, "black_clock": clock["black_ms"] if clock else 0}
    elapsed = int((time.time() - clock["last_move_time"]) * 1000)
    white_ms = clock["white_ms"] - (elapsed if clock["active"] == "white" else 0)
    black_ms = clock["black_ms"] - (elapsed if clock["active"] == "black" else 0)
    return {"white_clock": max(0, white_ms), "black_clock": max(0, black_ms)}


def _deduct_and_switch(room_key: str) -> dict[str, int]:
    clock = room_clocks.get(room_key)
    if not clock or not clock.get("started"):
        return _get_clocks(room_key)
    now = time.time()
    elapsed = int((now - clock["last_move_time"]) * 1000)
    if clock["active"] == "white":
        clock["white_ms"] = max(0, clock["white_ms"] - elapsed + clock["increment_ms"])
        clock["active"] = "black"
    else:
        clock["black_ms"] = max(0, clock["black_ms"] - elapsed + clock["increment_ms"])
        clock["active"] = "white"
    clock["last_move_time"] = now
    return {"white_clock": clock["white_ms"], "black_clock": clock["black_ms"]}


def _get_active_color(room_key: str) -> str:
    """Which color should move next (from game state turn)."""
    state = room_states.get(room_key)
    if not state:
        return "white"
    turn = state.get("turn", "white")
    # Map game turn to color: for gomoku, "black" = player 1 (color "black")
    return turn


# --- Handlers ---

async def _handle_ready(room_key: str, conn: PlayerConnection, room_id: uuid.UUID) -> None:
    if conn.role == "spectator":
        return

    room_ready[room_key].add(conn.player_id)
    count = len(room_ready[room_key])
    await _broadcast(room_key, {"type": "ready_status", "ready_count": count, "needed": 2})

    if count >= 2:
        # Countdown
        for i in range(5, 0, -1):
            await _broadcast(room_key, {"type": "countdown", "seconds": i})
            await asyncio.sleep(1)

        # Init game
        state = room_states.get(room_key)
        game_type = state["game_type"] if state else "chess"
        init = await get_initial_state(game_type)
        room_states[room_key] = {
            "fen": init.get("fen", ""),
            "turn": init.get("turn", "white"),
            "game_over": False,
            "game_type": game_type,
            "started": True,
        }

        # Init clock
        clock = room_clocks.get(room_key, {})
        clock["started"] = True
        clock["last_move_time"] = time.time()
        clock["active"] = init.get("turn", "white")
        room_clocks[room_key] = clock

        clocks = _get_clocks(room_key)
        await _broadcast(room_key, {"type": "game_start", "fen": room_states[room_key]["fen"], "turn": room_states[room_key]["turn"], **clocks})

        # Persist
        await redis_store.save_game_state(room_key, room_states[room_key])
        c = room_clocks[room_key]
        await redis_store.save_clock(room_key, c["white_ms"], c["black_ms"], c["active"], c["last_move_time"], c["increment_ms"], True)

        asyncio.create_task(_clock_checker(room_key, room_id))


async def _handle_move(room_key: str, message: dict, conn: PlayerConnection, room_id: uuid.UUID) -> None:
    state = room_states.get(room_key)
    if not state or not state.get("started"):
        await _send(conn.ws, {"type": "error", "message": "Ván đấu chưa bắt đầu"})
        return
    if state["game_over"]:
        await _send(conn.ws, {"type": "error", "message": "Ván đấu đã kết thúc"})
        return
    if conn.role == "spectator":
        await _send(conn.ws, {"type": "error", "message": "Khán giả không thể đi nước"})
        return

    # Turn enforcement
    active_color = _get_active_color(room_key)
    if conn.role != active_color:
        await _send(conn.ws, {"type": "error", "message": "Chưa đến lượt bạn"})
        return

    # Check timeout
    clocks = _get_clocks(room_key)
    if clocks["white_clock"] <= 0:
        await _end_game(room_key, room_id, "black_win", "timeout")
        return
    if clocks["black_clock"] <= 0:
        await _end_game(room_key, room_id, "white_win", "timeout")
        return

    # Validate
    result = await validate_move(state["game_type"], state["fen"], message)
    if not result.valid:
        await _send(conn.ws, {"type": "error", "message": "Nước đi không hợp lệ"})
        return

    # Update state
    state["fen"] = result.new_fen
    state["turn"] = result.turn
    state["game_over"] = result.game_over

    # Update clock
    new_clocks = _deduct_and_switch(room_key)

    # Broadcast
    response: dict[str, Any] = {
        "type": "move",
        **{k: v for k, v in message.items() if k != "type"},
        "fen": result.new_fen,
        "turn": result.turn,
        **new_clocks,
    }
    await _broadcast(room_key, response)

    # Persist
    await redis_store.save_game_state(room_key, state)
    c = room_clocks.get(room_key)
    if c:
        await redis_store.save_clock(room_key, c["white_ms"], c["black_ms"], c["active"], c["last_move_time"], c["increment_ms"], c["started"])

    if result.game_over:
        await _end_game(room_key, room_id, result.result or "draw", result.reason or "unknown")


async def _end_game(room_key: str, room_id: uuid.UUID, result: str, reason: str) -> None:
    state = room_states.get(room_key)
    if state:
        state["game_over"] = True
    clock = room_clocks.get(room_key)
    if clock:
        clock["started"] = False

    clocks = _get_clocks(room_key)
    await _broadcast(room_key, {"type": "game_over", "result": result, "reason": reason, **clocks})
    await redis_store.delete_room(room_key)
    asyncio.create_task(_save_game_result(room_id, result))


async def _save_game_result(room_id: uuid.UUID, result: str) -> None:
    from app.db.session import async_session_factory
    from app.modules.games.models import GameRoomStatus
    from app.modules.games.repository import GameRepository
    try:
        async with async_session_factory() as db:
            repo = GameRepository(db)
            room = await repo.get_room_by_id(room_id)
            if room and room.status != GameRoomStatus.finished:
                room.status = GameRoomStatus.finished
                room.result = result
                await db.commit()
    except Exception as exc:
        logger.error("Save game result failed: %s", exc)


async def _clock_checker(room_key: str, room_id: uuid.UUID) -> None:
    while True:
        await asyncio.sleep(1)
        state = room_states.get(room_key)
        if not state or state.get("game_over") or not state.get("started"):
            return
        clocks = _get_clocks(room_key)
        if clocks["white_clock"] <= 0:
            await _end_game(room_key, room_id, "black_win", "timeout")
            return
        if clocks["black_clock"] <= 0:
            await _end_game(room_key, room_id, "white_win", "timeout")
            return


# --- Auth helper ---

async def _resolve_player(token: str | None) -> str | None:
    """Resolve JWT token to member_id."""
    if not token:
        return None
    try:
        from jose import jwt
        from app.core.config import settings
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload.get("member_id")
    except Exception:
        return None


# --- Main endpoint ---

@ws_router.websocket("/ws/game/{room_id}")
async def game_websocket(websocket: WebSocket, room_id: uuid.UUID, token: str = Query(default="")):
    await websocket.accept()
    room_key = str(room_id)

    # Authenticate
    player_id = await _resolve_player(token)

    # Determine role
    role = "spectator"
    from app.db.session import async_session_factory
    from app.modules.games.repository import GameRepository
    try:
        async with async_session_factory() as db:
            repo = GameRepository(db)
            room = await repo.get_room_by_id(room_id)
            if room:
                if player_id and str(room.white_player_id) == player_id:
                    role = "white"
                elif player_id and str(room.black_player_id) == player_id:
                    role = "black"

                # Init clock if needed
                if room_key not in room_clocks:
                    redis_state = await redis_store.get_game_state(room_key)
                    redis_clock = await redis_store.get_clock(room_key)
                    if redis_state and redis_clock:
                        room_states[room_key] = redis_state
                        room_clocks[room_key] = redis_clock
                        if redis_state.get("started") and not redis_state.get("game_over"):
                            asyncio.create_task(_clock_checker(room_key, room_id))
                    else:
                        room_clocks[room_key] = {
                            "white_ms": room.time_control * 1000,
                            "black_ms": room.time_control * 1000,
                            "increment_ms": room.increment * 1000,
                            "active": "white",
                            "last_move_time": 0,
                            "started": False,
                        }
                        room_states[room_key] = {
                            "fen": room.fen or "",
                            "turn": "white",
                            "game_over": False,
                            "game_type": room.game_type,
                            "started": False,
                        }
    except Exception as exc:
        logger.error("WS init failed: %s", exc)

    conn = PlayerConnection(websocket, player_id, role)
    room_connections[room_key].append(conn)

    # Send current state
    state = room_states.get(room_key)
    clocks = _get_clocks(room_key)
    await _send(websocket, {
        "type": "state" if (state and state.get("started")) else "waiting",
        "role": role,
        "players_connected": sum(1 for c in room_connections[room_key] if c.role in ("white", "black")),
        "ready_count": len(room_ready[room_key]),
        **(state or {}),
        **clocks,
    })

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")

            if msg_type == "ready":
                await _handle_ready(room_key, conn, room_id)

            elif msg_type == "unready":
                if conn.player_id:
                    room_ready[room_key].discard(conn.player_id)
                    await _broadcast(room_key, {"type": "ready_status", "ready_count": len(room_ready[room_key]), "needed": 2})

            elif msg_type == "move":
                await _handle_move(room_key, message, conn, room_id)

            elif msg_type == "resign":
                if conn.role in ("white", "black") and state and state.get("started"):
                    result = "black_win" if conn.role == "white" else "white_win"
                    await _end_game(room_key, room_id, result, "resign")

            elif msg_type == "draw_offer":
                if conn.role in ("white", "black"):
                    # Send only to opponent
                    for c in room_connections[room_key]:
                        if c.role in ("white", "black") and c.role != conn.role:
                            await _send(c.ws, {"type": "draw_offered"})

            elif msg_type == "draw_accept":
                if conn.role in ("white", "black"):
                    await _end_game(room_key, room_id, "draw", "agreement")

            elif msg_type == "chat":
                await _broadcast(room_key, {"type": "chat", "message": message.get("message", ""), "sender": conn.role})

    except WebSocketDisconnect:
        room_connections[room_key].remove(conn)
        if conn.player_id:
            room_ready[room_key].discard(conn.player_id)

        players_left = sum(1 for c in room_connections[room_key] if c.role in ("white", "black"))
        await _broadcast(room_key, {"type": "player_disconnected", "role": conn.role, "players_connected": players_left})

        if not room_connections[room_key]:
            del room_connections[room_key]
            room_ready.pop(room_key, None)
            state = room_states.get(room_key)
            if not state or not state.get("started"):
                room_states.pop(room_key, None)
                room_clocks.pop(room_key, None)
