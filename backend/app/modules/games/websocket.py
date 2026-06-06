"""WebSocket handler for real-time gameplay.

Validation is delegated to Analysis Services (Stockfish/Pikafish/KataGo).
Backend chỉ giữ FEN state và relay messages.
"""
import asyncio
import json
import logging
import uuid
from collections import defaultdict
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.modules.games.validation_client import get_initial_state, validate_move

logger = logging.getLogger(__name__)

ws_router = APIRouter()

# In-memory state (production: use Redis)
rooms: dict[str, list[WebSocket]] = defaultdict(list)
room_states: dict[str, dict[str, Any]] = {}  # room_key -> {fen, turn, game_over, game_type}
room_ready: dict[str, set] = defaultdict(set)  # room_key -> set of ready websocket ids


async def _broadcast(room_key: str, message: dict) -> None:
    msg = json.dumps(message)
    for conn in rooms[room_key]:
        await conn.send_text(msg)


async def _broadcast_except(room_key: str, message: dict, exclude: WebSocket) -> None:
    msg = json.dumps(message)
    for conn in rooms[room_key]:
        if conn != exclude:
            await conn.send_text(msg)


async def _trigger_post_game_analysis(room_id: uuid.UUID) -> None:
    from app.db.session import async_session_factory
    from app.modules.games.repository import GameRepository
    from app.modules.games.service import GameService

    try:
        async with async_session_factory() as db:
            repo = GameRepository(db)
            service = GameService(repo)
            await service.review_game(room_id)
            await db.commit()
            logger.info("Post-game analysis completed for room %s", room_id)
    except Exception as exc:
        logger.warning("Post-game analysis failed for room %s: %s", room_id, exc)


def _cleanup_room(room_key: str) -> None:
    room_states.pop(room_key, None)


async def _abort_abandoned_room(room_id: uuid.UUID) -> None:
    """Mark room as aborted/draw if all players disconnected."""
    from app.db.session import async_session_factory
    from app.modules.games.models import GameRoomStatus
    from app.modules.games.repository import GameRepository

    await asyncio.sleep(30)  # Grace period — wait 30s in case they reconnect

    # Check if anyone reconnected
    room_key = str(room_id)
    if room_key in rooms and rooms[room_key]:
        return  # Someone reconnected

    try:
        async with async_session_factory() as db:
            repo = GameRepository(db)
            room = await repo.get_room_by_id(room_id)
            if room and room.status == GameRoomStatus.playing:
                room.status = GameRoomStatus.finished
                room.result = "draw"
                await db.commit()
                logger.info("Room %s abandoned — marked as draw", room_id)
    except Exception as exc:
        logger.error("Failed to abort abandoned room %s: %s", room_id, exc)


async def _init_room(room_key: str, game_type: str) -> dict[str, Any]:
    """Khởi tạo room state từ analysis service."""
    state = await get_initial_state(game_type)
    room_states[room_key] = {
        "fen": state.get("fen", ""),
        "turn": state.get("turn", "white"),
        "game_over": False,
        "game_type": game_type,
        "started": False,
    }
    return {"type": "state", "game_type": game_type, **room_states[room_key]}


async def _handle_ready(room_key: str, websocket: WebSocket, room_id: uuid.UUID) -> None:
    """Player marks ready. When both ready → 5s countdown → start."""
    ws_id = id(websocket)
    room_ready[room_key].add(ws_id)

    await _broadcast(room_key, {"type": "ready_status", "ready_count": len(room_ready[room_key]), "needed": 2})

    if len(room_ready[room_key]) >= 2:
        # Both ready → countdown
        for i in range(5, 0, -1):
            await _broadcast(room_key, {"type": "countdown", "seconds": i})
            await asyncio.sleep(1)

        # Start game
        state = room_states.get(room_key)
        if state:
            state["started"] = True

        # Init game state if not already
        if not state or not state.get("fen"):
            game_type = state.get("game_type", "chess") if state else "chess"
            init_state = await get_initial_state(game_type)
            room_states[room_key] = {
                "fen": init_state.get("fen", ""),
                "turn": init_state.get("turn", "white"),
                "game_over": False,
                "game_type": game_type,
                "started": True,
            }

        await _broadcast(room_key, {"type": "game_start", "fen": room_states[room_key]["fen"], "turn": room_states[room_key]["turn"]})


async def _handle_move(room_key: str, message: dict, websocket: WebSocket, room_id: uuid.UUID) -> None:
    """Validate move qua analysis service, broadcast kết quả."""
    state = room_states.get(room_key)
    if not state:
        await websocket.send_text(json.dumps({"type": "error", "message": "Room chưa khởi tạo"}))
        return

    if state["game_over"]:
        await websocket.send_text(json.dumps({"type": "error", "message": "Ván đấu đã kết thúc"}))
        return

    game_type = state["game_type"]
    fen = state["fen"]

    # Gọi analysis service validate
    result = await validate_move(game_type, fen, message)

    if not result.valid:
        await websocket.send_text(json.dumps({"type": "error", "message": "Nước đi không hợp lệ"}))
        return

    # Cập nhật state
    state["fen"] = result.new_fen
    state["turn"] = result.turn
    state["game_over"] = result.game_over

    # Broadcast move
    response: dict[str, Any] = {
        "type": "move",
        **{k: v for k, v in message.items() if k != "type"},
        "fen": result.new_fen,
        "turn": result.turn,
    }
    if result.captures:
        response["captures"] = result.captures

    await _broadcast(room_key, response)

    # Handle game over
    if result.game_over:
        game_over_msg: dict[str, Any] = {
            "type": "game_over",
            "result": result.result or "draw",
            "reason": result.reason or "unknown",
        }
        if result.score:
            game_over_msg["score"] = result.score
        await _broadcast(room_key, game_over_msg)
        asyncio.create_task(_trigger_post_game_analysis(room_id))


async def _handle_pass(room_key: str, websocket: WebSocket, room_id: uuid.UUID) -> None:
    """Handle pass (Go only)."""
    state = room_states.get(room_key)
    if not state or state["game_type"] != "go":
        return

    result = await validate_move("go", state["fen"], {"action": "pass"})

    state["fen"] = result.new_fen
    state["turn"] = result.turn
    state["game_over"] = result.game_over

    response: dict[str, Any] = {"type": "pass", "fen": result.new_fen, "turn": result.turn}
    await _broadcast(room_key, response)

    if result.game_over:
        game_over_msg: dict[str, Any] = {
            "type": "game_over",
            "result": result.result or "draw",
            "reason": result.reason or "double_pass",
        }
        if result.score:
            game_over_msg["score"] = result.score
        await _broadcast(room_key, game_over_msg)
        asyncio.create_task(_trigger_post_game_analysis(room_id))


@ws_router.websocket("/ws/game/{room_id}")
async def game_websocket(websocket: WebSocket, room_id: uuid.UUID):
    await websocket.accept()
    room_key = str(room_id)
    rooms[room_key].append(websocket)

    # Gửi state hiện tại (hoặc default nếu chưa init)
    state = room_states.get(room_key)
    if state:
        await websocket.send_text(json.dumps({"type": "state", **state}))
    else:
        await websocket.send_text(json.dumps({"type": "waiting_init"}))

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type")

            if msg_type == "init":
                game_type = message.get("game_type", "chess")
                state_msg = await _init_room(room_key, game_type)
                await _broadcast(room_key, state_msg)

            elif msg_type == "ready":
                await _handle_ready(room_key, websocket, room_id)

            elif msg_type == "move":
                state = room_states.get(room_key)
                if state and not state.get("started"):
                    await websocket.send_text(json.dumps({"type": "error", "message": "Ván đấu chưa bắt đầu. Hãy nhấn Sẵn sàng."}))
                else:
                    await _handle_move(room_key, message, websocket, room_id)

            elif msg_type == "pass":
                await _handle_pass(room_key, websocket, room_id)

            elif msg_type == "resign":
                await _broadcast_except(room_key, {"type": "resign", "by": "opponent"}, websocket)
                _cleanup_room(room_key)

            elif msg_type == "draw_offer":
                await _broadcast_except(room_key, {"type": "draw_offered"}, websocket)

            elif msg_type == "draw_accept":
                await _broadcast(room_key, {"type": "game_over", "result": "draw", "reason": "agreement"})
                _cleanup_room(room_key)

            elif msg_type == "chat":
                await _broadcast(room_key, {"type": "chat", "message": message.get("message", ""), "sender": "player"})

    except WebSocketDisconnect:
        rooms[room_key].remove(websocket)
        room_ready[room_key].discard(id(websocket))
        if not rooms[room_key]:
            del rooms[room_key]
            room_ready.pop(room_key, None)
            _cleanup_room(room_key)
            # All players disconnected — abort if still playing
            asyncio.create_task(_abort_abandoned_room(room_id))
