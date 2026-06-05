"""Tests cho Play vs Human flow (game rooms, join, WebSocket)."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestPlayHuman:
    """Test human game lifecycle: create room → join → play."""

    async def test_create_room(self, client: AsyncClient, auth_headers: dict):
        """Tạo phòng chơi mới."""
        resp = await client.post("/api/v1/games", json={
            "game_type": "chess", "time_control": 300, "increment": 2,
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["game_type"] == "chess"
        assert data["time_control"] == 300
        assert data["increment"] == 2
        assert data["status"] == "waiting"
        assert data["white_player_id"] is not None
        assert data["black_player_id"] is None

    async def test_join_room(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """Player 2 join phòng → status chuyển sang playing."""
        # Player 1 creates room
        create_resp = await client.post("/api/v1/games", json={
            "game_type": "chess", "time_control": 300, "increment": 0,
        }, headers=auth_headers)
        room_id = create_resp.json()["data"]["id"]

        # Player 2 joins
        join_resp = await client.post(f"/api/v1/games/{room_id}/join", headers=second_user_headers)
        assert join_resp.status_code == 200
        data = join_resp.json()["data"]
        assert data["status"] == "playing"
        assert data["black_player_id"] is not None

    async def test_cannot_join_own_room(self, client: AsyncClient, auth_headers: dict):
        """Không thể tự join phòng mình tạo."""
        create_resp = await client.post("/api/v1/games", json={
            "game_type": "chess", "time_control": 300, "increment": 0,
        }, headers=auth_headers)
        room_id = create_resp.json()["data"]["id"]

        join_resp = await client.post(f"/api/v1/games/{room_id}/join", headers=auth_headers)
        assert join_resp.status_code == 400

    async def test_cannot_join_started_room(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """Không thể join phòng đã bắt đầu."""
        create_resp = await client.post("/api/v1/games", json={
            "game_type": "chess", "time_control": 300, "increment": 0,
        }, headers=auth_headers)
        room_id = create_resp.json()["data"]["id"]

        # Player 2 joins (room starts)
        await client.post(f"/api/v1/games/{room_id}/join", headers=second_user_headers)

        # Player 3 tries to join (register another user)
        await client.post("/api/v1/auth/register", json={
            "email": "player3@vinamilk.com.vn", "password": "testpass123", "full_name": "Player Three",
        })
        login_resp = await client.post("/api/v1/auth/login", json={
            "email": "player3@vinamilk.com.vn", "password": "testpass123",
        })
        p3_headers = {"Authorization": f"Bearer {login_resp.json()['data']['access_token']}"}

        join_resp = await client.post(f"/api/v1/games/{room_id}/join", headers=p3_headers)
        assert join_resp.status_code == 400

    async def test_live_rooms(self, client: AsyncClient, auth_headers: dict):
        """Danh sách phòng live hiển thị phòng đang chờ."""
        await client.post("/api/v1/games", json={
            "game_type": "chess", "time_control": 300, "increment": 0,
        }, headers=auth_headers)

        resp = await client.get("/api/v1/games/live", headers=auth_headers)
        assert resp.status_code == 200
        rooms = resp.json()["data"]
        assert len(rooms) >= 1
        assert any(r["status"] == "waiting" for r in rooms)

    async def test_get_room_details(self, client: AsyncClient, auth_headers: dict):
        """Lấy thông tin phòng theo ID."""
        create_resp = await client.post("/api/v1/games", json={
            "game_type": "xiangqi", "time_control": 600, "increment": 5,
        }, headers=auth_headers)
        room_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/games/{room_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["game_type"] == "xiangqi"
        assert data["time_control"] == 600
        assert data["increment"] == 5

    async def test_create_room_from_match(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """Tạo phòng từ ván đấu giải (tournament integration)."""
        # Create tournament
        t_resp = await client.post("/api/v1/tournaments", json={
            "name": "Test Cup", "game_type": "chess", "time_format": "blitz",
            "format": "round_robin", "mode": "online", "max_participants": 4,
        }, headers=auth_headers)
        t_id = t_resp.json()["data"]["id"]

        # Get member IDs
        me_resp = await client.get("/api/v1/auth/me", headers=auth_headers)
        p1_member = me_resp.json()["data"]["member_id"]
        me2_resp = await client.get("/api/v1/auth/me", headers=second_user_headers)
        p2_member = me2_resp.json()["data"]["member_id"]

        # Register participants
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": p1_member}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": p2_member}, headers=auth_headers)

        # Generate pairings
        await client.post(f"/api/v1/tournaments/{t_id}/generate-pairings", headers=auth_headers)

        # Get rounds to find a match
        rounds_resp = await client.get(f"/api/v1/tournaments/{t_id}/rounds", headers=auth_headers)
        rounds = rounds_resp.json()["data"]
        assert len(rounds) > 0
        match_id = rounds[0]["matches"][0]["id"]

        # Create room from match
        room_resp = await client.post(f"/api/v1/games/from-match/{match_id}", headers=auth_headers)
        assert room_resp.status_code == 201
        room = room_resp.json()["data"]
        assert room["match_id"] == match_id
        assert room["status"] == "waiting"
