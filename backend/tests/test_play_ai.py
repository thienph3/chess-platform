"""Tests cho Play vs AI flow."""
import pytest
from httpx import AsyncClient

from app.modules.games.ai_router import AI_PLAYER_ID


@pytest.mark.asyncio
class TestPlayAI:
    """Test AI game lifecycle: start → play → end."""

    async def test_start_game_white(self, client: AsyncClient, auth_headers: dict):
        """Player chọn cầm trắng → AI cầm đen, không có ai_first_move."""
        resp = await client.post("/api/v1/games/ai/start", json={
            "game_type": "chess", "difficulty": "medium",
            "time_control": 600, "increment": 0, "player_color": "white",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["player_color"] == "white"
        assert data["room_id"] is not None
        assert data["fen"] != ""
        assert data["ai_first_move"] is None

    async def test_start_game_black(self, client: AsyncClient, auth_headers: dict):
        """Player chọn cầm đen → AI đi trước, có ai_first_move."""
        resp = await client.post("/api/v1/games/ai/start", json={
            "game_type": "chess", "difficulty": "easy",
            "time_control": 300, "increment": 0, "player_color": "black",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["player_color"] == "black"
        # ai_first_move may be None if analysis service is unavailable
        # assert data["ai_first_move"] is not None  # requires analysis service

    async def test_start_game_random(self, client: AsyncClient, auth_headers: dict):
        """Player chọn random → color là white hoặc black."""
        resp = await client.post("/api/v1/games/ai/start", json={
            "game_type": "chess", "difficulty": "medium",
            "time_control": 600, "increment": 0, "player_color": "random",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["player_color"] in ("white", "black")

    async def test_play_valid_move(self, client: AsyncClient, auth_headers: dict):
        """Player đi nước hợp lệ → AI trả lời (requires analysis service)."""
        pytest.importorskip("httpx")
        start = await client.post("/api/v1/games/ai/start", json={
            "game_type": "chess", "difficulty": "easy",
            "time_control": 600, "increment": 0, "player_color": "white",
        }, headers=auth_headers)
        room_id = start.json()["data"]["room_id"]

        # Play e2e4 — may fail if analysis service unavailable
        resp = await client.post("/api/v1/games/ai/play", json={
            "room_id": room_id,
            "move": {"from": "e2", "to": "e4"},
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        # valid=False when analysis service is down (graceful degradation)
        if data["valid"]:
            assert data["ai_move"] is not None
            assert data["ai_fen"] is not None
            assert data["game_over"] is False

    async def test_play_invalid_move(self, client: AsyncClient, auth_headers: dict):
        """Player đi nước không hợp lệ → valid=False."""
        start = await client.post("/api/v1/games/ai/start", json={
            "game_type": "chess", "difficulty": "easy",
            "time_control": 600, "increment": 0, "player_color": "white",
        }, headers=auth_headers)
        room_id = start.json()["data"]["room_id"]

        # Invalid move: e2 to e5 (pawn can't jump 3 squares)
        resp = await client.post("/api/v1/games/ai/play", json={
            "room_id": room_id,
            "move": {"from": "e2", "to": "e5"},
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["valid"] is False

    async def test_resign(self, client: AsyncClient, auth_headers: dict):
        """Player đầu hàng → game kết thúc, AI thắng."""
        start = await client.post("/api/v1/games/ai/start", json={
            "game_type": "chess", "difficulty": "easy",
            "time_control": 600, "increment": 0, "player_color": "white",
        }, headers=auth_headers)
        room_id = start.json()["data"]["room_id"]

        resp = await client.post("/api/v1/games/ai/resign",
            params={"room_id": room_id}, headers=auth_headers)
        assert resp.status_code == 200

        # Verify room is finished
        room_resp = await client.get(f"/api/v1/games/{room_id}", headers=auth_headers)
        room = room_resp.json()["data"]
        assert room["status"] == "finished"
        assert room["result"] == "black_win"  # AI (black) wins

    async def test_game_saved_in_history(self, client: AsyncClient, auth_headers: dict):
        """Ván AI được lưu vào DB, xuất hiện trong history."""
        start = await client.post("/api/v1/games/ai/start", json={
            "game_type": "chess", "difficulty": "easy",
            "time_control": 600, "increment": 0, "player_color": "white",
        }, headers=auth_headers)
        room_id = start.json()["data"]["room_id"]

        # Play 1 move then resign
        await client.post("/api/v1/games/ai/play", json={
            "room_id": room_id, "move": {"from": "e2", "to": "e4"},
        }, headers=auth_headers)
        await client.post("/api/v1/games/ai/resign",
            params={"room_id": room_id}, headers=auth_headers)

        # Check history
        resp = await client.get("/api/v1/games/history/all", headers=auth_headers)
        games = resp.json()["data"]
        assert any(g["id"] == room_id for g in games)

    async def test_ai_player_id_is_fixed(self, client: AsyncClient, auth_headers: dict):
        """AI luôn dùng UUID cố định."""
        start = await client.post("/api/v1/games/ai/start", json={
            "game_type": "chess", "difficulty": "medium",
            "time_control": 600, "increment": 0, "player_color": "white",
        }, headers=auth_headers)
        room_id = start.json()["data"]["room_id"]

        room_resp = await client.get(f"/api/v1/games/{room_id}", headers=auth_headers)
        room = room_resp.json()["data"]
        assert room["black_player_id"] == str(AI_PLAYER_ID)
