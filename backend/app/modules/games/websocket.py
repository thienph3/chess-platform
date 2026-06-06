"""WebSocket handler for real-time gameplay.

Flow: join → ready → countdown → playing (server clock) → finished
"""
import asyncio
import json
import logging
import time
import uuid
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.modules.games.validation_client import get_initial_state, validate_move
from app.modules.games import redis_store

logger = logging.getLogger(__name__)

ws_router = APIRouter()


# --- In-memory state (production: use Redis) ---

rooms: dict[str, list[WebSocket]] = defaultdict(list)

room_states: dict[str, dict[str, Any]] = {}
# {fen, turn, game_over, game_type, started}

room_ready: dict[str, set] = defaultdict(set)
# set of websocket ids that are ready

room_clocks: dict[str, dict[str, Any]] = {}
# {white_ms, black_ms, active: "white"|"black", last_move_time, increment_ms, started}


# --- Helpers ---

async def _broadcast(room_key: str, message: dict) -> None:
    msg = json.dumps(message)
    for conn in rooms[room_key]:
        try:
            await conn.send_text(msg)
        except Exception:
            pass


async def _send(ws: WebSocket, message: dict) -> None:
    try:
        await ws.send_text(json.dumps(message))
    except Exception:
        pass


def _get_clocks(room_key: str) -> dict[str, int]:
    """Get current clock values accounting for elapsed time."""
    clock = room_clocks.get(room_key)
    if not clock or not clock.get("started"):
        return {"white_clock": clock["white_ms"] if clock else 0, "black_clock": clock["black_ms"] if clock else 0}

    elapsed = int((time.time() - clock["last_move_time"]) * 1000)
    white_ms = clock["white_ms"]
    black_ms = clock["black_ms"]

    if clock["active"] == "white":
        white_ms = max(0, white_ms - elapsed)
    else:
        black_ms = max(0, black_ms - elapsed)

    return {"white_clock": white_ms, "black_clock": black_ms}


def _deduct_and_switch(room_key: str) -> dict[str, int]:
    """Deduct elapsed time from active player, add increment, switch turn."""
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


# --- Handlers ---

async def _handle_ready(room_key: str, websocket: WebSocket, room_id: uuid.UUID) -> None:
    """Player marks ready. Both ready → 5s countdown → start."""
    room_ready[room_key].add(id(websocket))
    await _broadcast(room_key, {"type": "ready_status", "ready_count": len(room_ready[room_key]), "needed": 2})

    if len(room_ready[room_key]) >= 2 and len(rooms[room_key]) >= 2:
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
        clock["active"] = "white"  # white moves first (or black for gomoku, handled by turn)
        room_clocks[room_key] = clock

        clocks = _get_clocks(room_key)
        await _broadcast(room_key, {
            "type": "game_start",
            "fen": room_states[room_key]["fen"],
            "turn": room_states[room_key]["turn"],
            **clocks,
        })

        # Persist to Redis
        await redis_store.save_game_state(room_key, room_states[room_key])
        c = room_clocks[room_key]
        await redis_store.save_clock(room_key, c["white_ms"], c["black_ms"], c["active"], c["last_move_time"], c["increment_ms"], True)

        # Start clock checker
        asyncio.create_task(_clock_checker(room_key, room_id))


async def _handle_unready(room_key: str, websocket: WebSocket) -> None:
    room_ready[room_key].discard(id(websocket))
    await _broadcast(room_key, {"type": "ready_status", "ready_count": len(room_ready[room_key]), "needed": 2})


async def _handle_move(room_key: str, message: dict, websocket: WebSocket, room_id: uuid.UUID) -> None:
    state = room_states.get(room_key)
    if not state or not state.get("started"):
        await _send(websocket, {"type": "error", "message": "Ván đấu chưa bắt đầu"})
        return
    if state["game_over"]:
        await _send(websocket, {"type": "error", "message": "Ván đấu đã kết thúc"})
        return

    # Check timeout before processing
    clocks = _get_clocks(room_key)
    clock = room_clocks.get(room_key)
    if clock and clocks["white_clock"] <= 0:
        await _end_game(room_key, room_id, "black_win", "timeout")
        return
    if clock and clocks["black_clock"] <= 0:
        await _end_game(room_key, room_id, "white_win", "timeout")
        return

    # Validate move
    result = await validate_move(state["game_type"], state["fen"], message)
    if not result.valid:
        await _send(websocket, {"type": "error", "message": "Nước đi không hợp lệ"})
        return

    # Update state
    state["fen"] = result.new_fen
    state["turn"] = result.turn
    state["game_over"] = result.game_over

    # Update clock
    new_clocks = _deduct_and_switch(room_key)

    # Broadcast move
    response: dict[str, Any] = {
        "type": "move",
        **{k: v for k, v in message.items() if k != "type"},
        "fen": result.new_fen,
        "turn": result.turn,
        **new_clocks,
    }
    await _broadcast(room_key, response)

    # Persist state to Redis
    await redis_store.save_game_state(room_key, state)
    c = room_clocks.get(room_key)
    if c:
        await redis_store.save_clock(room_key, c["white_ms"], c["black_ms"], c["active"], c["last_move_time"], c["increment_ms"], c["started"])

    # Game over by rules
    if result.game_over:
        await _end_game(room_key, room_id, result.result or "draw", result.reason or "unknown")


async def _end_game(room_key: str, room_id: uuid.UUID, result: str, reason: str) -> None:
    """End the game and update DB."""
    state = room_states.get(room_key)
    if state:
        state["game_over"] = True

    clock = room_clocks.get(room_key)
    if clock:
        clock["started"] = False

    clocks = _get_clocks(room_key)
    await _broadcast(room_key, {"type": "game_over", "result": result, "reason": reason, **clocks})

    # Clean up Redis
    await redis_store.delete_room(room_key)

    # Update DB
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
    """Check clock every second, end game if time runs out."""
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


# --- Main WebSocket endpoint ---

@ws_router.websocket("/ws/game/{room_id}")
async def game_websocket(websocket: WebSocket, room_id: uuid.UUID):
    await websocket.accept()
    room_key = str(room_id)
    rooms[room_key].append(websocket)

    # Init clock from DB if not exists
    if room_key not in room_clocks:
        # Try Redis first (survives pod restart)
        redis_state = await redis_store.get_game_state(room_key)
        redis_clock = await redis_store.get_clock(room_key)
        if redis_state and redis_clock:
            room_states[room_key] = redis_state
            room_clocks[room_key] = redis_clock
            if redis_state.get("started") and not redis_state.get("game_over"):
                asyncio.create_task(_clock_checker(room_key, room_id))
        else:
            # Fallback: load from DB
            from app.db.session import async_session_factory
            from app.modules.games.repository import GameRepository
            try:
                async with async_session_factory() as db:
                    repo = GameRepository(db)
                    room = await repo.get_room_by_id(room_id)
                    if room:
                        room_clocks[room_key] = {
                            "white_ms": room.time_control * 1000,
                            "black_ms": room.time_control * 1000,
                            "increment_ms": room.increment * 1000,
                            "active": "white",
                            "last_move_time": 0,
                            "started": False,
                        }
                        if room_key not in room_states:
                            room_states[room_key] = {
                                "fen": room.fen or "",
                                "turn": "white",
                                "game_over": False,
                                "game_type": room.game_type,
                                "started": False,
                            }
            except Exception as exc:
                logger.error("Failed to load room: %s", exc)

    # Send current state
    state = room_states.get(room_key)
    clocks = _get_clocks(room_key)
    if state and state.get("started"):
        await _send(websocket, {"type": "state", **state, **clocks})
    else:
        await _send(websocket, {
            "type": "waiting",
            "players_connected": len(rooms[room_key]),
            "ready_count": len(room_ready[room_key]),
            **clocks,
        })

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")

            if msg_type == "init":
                game_type = message.get("game_type", "chess")
                state = room_states.get(room_key)
                if state:
                    state["game_type"] = game_type
                await _broadcast(room_key, {"type": "room_info", "game_type": game_type, "players_connected": len(rooms[room_key])})

            elif msg_type == "ready":
                await _handle_ready(room_key, websocket, room_id)

            elif msg_type == "unready":
                await _handle_unready(room_key, websocket)

            elif msg_type == "move":
                await _handle_move(room_key, message, websocket, room_id)

            elif msg_type == "resign":
                state = room_states.get(room_key)
                if state and state.get("started"):
                    # Determine who resigned
                    idx = rooms[room_key].index(websocket)
                    result = "black_win" if idx == 0 else "white_win"
                    await _end_game(room_key, room_id, result, "resign")
                else:
                    await _broadcast(room_key, {"type": "resign", "by": "opponent"})

            elif msg_type == "draw_offer":
                await _broadcast(room_key, {"type": "draw_offered"})

            elif msg_type == "draw_accept":
                await _end_game(room_key, room_id, "draw", "agreement")

            elif msg_type == "chat":
                await _broadcast(room_key, {"type": "chat", "message": message.get("message", ""), "sender": "player"})

    except WebSocketDisconnect:
        rooms[room_key].remove(websocket)
        room_ready[room_key].discard(id(websocket))

        # Notify remaining players
        await _broadcast(room_key, {"type": "player_disconnected", "players_connected": len(rooms[room_key])})

        if not rooms[room_key]:
            del rooms[room_key]
            room_ready.pop(room_key, None)
            state = room_states.get(room_key)
            if not state or not state.get("started"):
                # Not started yet — clean up
                room_states.pop(room_key, None)
                room_clocks.pop(room_key, None)
            # If started, clock keeps ticking — _clock_checker will handle timeout
