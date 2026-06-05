"""Tests cho Tournament flow: create, register, pair, play, result."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestTournament:
    """Test tournament lifecycle."""

    async def test_create_tournament(self, client: AsyncClient, auth_headers: dict):
        """Tạo giải đấu mới."""
        resp = await client.post("/api/v1/tournaments", json={
            "name": "VCC Blitz #1", "game_type": "chess", "time_format": "blitz",
            "format": "swiss", "mode": "online", "max_participants": 8,
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["name"] == "VCC Blitz #1"
        assert data["mode"] == "online"
        assert data["status"] == "draft"

    async def test_create_otb_tournament(self, client: AsyncClient, auth_headers: dict):
        """Tạo giải OTB."""
        resp = await client.post("/api/v1/tournaments", json={
            "name": "VCC OTB Rapid", "game_type": "chess", "time_format": "rapid",
            "format": "round_robin", "mode": "otb", "max_participants": 6,
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["data"]["mode"] == "otb"

    async def test_register_participant(self, client: AsyncClient, auth_headers: dict):
        """Đăng ký tham gia giải."""
        # Create tournament
        t_resp = await client.post("/api/v1/tournaments", json={
            "name": "Test", "game_type": "chess", "time_format": "blitz",
            "format": "swiss", "mode": "online", "max_participants": 8,
        }, headers=auth_headers)
        t_id = t_resp.json()["data"]["id"]

        # Get member_id
        me = await client.get("/api/v1/auth/me", headers=auth_headers)
        member_id = me.json()["data"]["member_id"]

        # Register
        resp = await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": member_id}, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["data"]["member_id"] == member_id

    async def test_generate_round_robin_pairings(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """Generate pairings cho Round Robin."""
        t_resp = await client.post("/api/v1/tournaments", json={
            "name": "RR Test", "game_type": "chess", "time_format": "blitz",
            "format": "round_robin", "mode": "online", "max_participants": 4,
        }, headers=auth_headers)
        t_id = t_resp.json()["data"]["id"]

        # Register 2 players
        me = await client.get("/api/v1/auth/me", headers=auth_headers)
        me2 = await client.get("/api/v1/auth/me", headers=second_user_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": me.json()["data"]["member_id"]}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": me2.json()["data"]["member_id"]}, headers=auth_headers)

        # Generate pairings
        resp = await client.post(f"/api/v1/tournaments/{t_id}/generate-pairings", headers=auth_headers)
        assert resp.status_code == 200

        # Check rounds created
        rounds_resp = await client.get(f"/api/v1/tournaments/{t_id}/rounds", headers=auth_headers)
        rounds = rounds_resp.json()["data"]
        assert len(rounds) >= 1
        assert len(rounds[0]["matches"]) >= 1

    async def test_submit_match_result(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """Admin nhập kết quả OTB match."""
        # Setup tournament with pairings
        t_resp = await client.post("/api/v1/tournaments", json={
            "name": "OTB Test", "game_type": "chess", "time_format": "rapid",
            "format": "round_robin", "mode": "otb", "max_participants": 4,
        }, headers=auth_headers)
        t_id = t_resp.json()["data"]["id"]

        me = await client.get("/api/v1/auth/me", headers=auth_headers)
        me2 = await client.get("/api/v1/auth/me", headers=second_user_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": me.json()["data"]["member_id"]}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": me2.json()["data"]["member_id"]}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/generate-pairings", headers=auth_headers)

        # Get match ID
        rounds_resp = await client.get(f"/api/v1/tournaments/{t_id}/rounds", headers=auth_headers)
        match_id = rounds_resp.json()["data"][0]["matches"][0]["id"]

        # Submit result
        resp = await client.patch(f"/api/v1/matches/{match_id}/result", json={
            "result": "white_win", "pgn": "1. e4 e5 2. Nf3 Nc6 1-0",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["result"] == "white_win"

    async def test_submit_draw_result(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """Nhập kết quả hòa."""
        t_resp = await client.post("/api/v1/tournaments", json={
            "name": "Draw Test", "game_type": "xiangqi", "time_format": "rapid",
            "format": "round_robin", "mode": "otb", "max_participants": 4,
        }, headers=auth_headers)
        t_id = t_resp.json()["data"]["id"]

        me = await client.get("/api/v1/auth/me", headers=auth_headers)
        me2 = await client.get("/api/v1/auth/me", headers=second_user_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": me.json()["data"]["member_id"]}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": me2.json()["data"]["member_id"]}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/generate-pairings", headers=auth_headers)

        rounds_resp = await client.get(f"/api/v1/tournaments/{t_id}/rounds", headers=auth_headers)
        match_id = rounds_resp.json()["data"][0]["matches"][0]["id"]

        resp = await client.patch(f"/api/v1/matches/{match_id}/result", json={
            "result": "draw",
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["result"] == "draw"

    async def test_create_rooms_for_online_round(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """Admin tạo phòng cho round online → 2 players join và chơi."""
        t_resp = await client.post("/api/v1/tournaments", json={
            "name": "Online Test", "game_type": "chess", "time_format": "blitz",
            "format": "round_robin", "mode": "online", "max_participants": 4,
        }, headers=auth_headers)
        t_id = t_resp.json()["data"]["id"]

        me = await client.get("/api/v1/auth/me", headers=auth_headers)
        me2 = await client.get("/api/v1/auth/me", headers=second_user_headers)
        p1_id = me.json()["data"]["member_id"]
        p2_id = me2.json()["data"]["member_id"]
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": p1_id}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": p2_id}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/generate-pairings", headers=auth_headers)

        # Get round ID
        rounds_resp = await client.get(f"/api/v1/tournaments/{t_id}/rounds", headers=auth_headers)
        round_data = rounds_resp.json()["data"][0]
        round_id = round_data["id"]
        match_id = round_data["matches"][0]["id"]

        # Create rooms
        resp = await client.post(
            f"/api/v1/tournaments/{t_id}/rounds/{round_id}/create-rooms",
            headers=auth_headers,
        )
        assert resp.status_code == 200
        count = resp.json()["data"]
        assert count >= 1

        # Find the room created for this match
        room_resp = await client.post(f"/api/v1/games/from-match/{match_id}", headers=auth_headers)
        # Room might already exist from create-rooms, or this creates a new one
        room_id = room_resp.json()["data"]["id"]

        # Verify room has correct players
        room_detail = await client.get(f"/api/v1/games/{room_id}", headers=auth_headers)
        room = room_detail.json()["data"]
        assert room["status"] == "waiting"
        assert room["game_type"] == "chess"
        player_ids = {room["white_player_id"], room["black_player_id"]}
        assert p1_id in player_ids
        assert p2_id in player_ids

        # Verify moves endpoint works (empty at start)
        moves_resp = await client.get(f"/api/v1/games/{room_id}/moves", headers=auth_headers)
        assert moves_resp.status_code == 200
        assert moves_resp.json()["data"] == []

    async def test_tournament_standings(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """Bảng xếp hạng sau khi có kết quả."""
        t_resp = await client.post("/api/v1/tournaments", json={
            "name": "Standings Test", "game_type": "chess", "time_format": "blitz",
            "format": "round_robin", "mode": "otb", "max_participants": 4,
        }, headers=auth_headers)
        t_id = t_resp.json()["data"]["id"]

        me = await client.get("/api/v1/auth/me", headers=auth_headers)
        me2 = await client.get("/api/v1/auth/me", headers=second_user_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": me.json()["data"]["member_id"]}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": me2.json()["data"]["member_id"]}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/generate-pairings", headers=auth_headers)

        # Submit result
        rounds_resp = await client.get(f"/api/v1/tournaments/{t_id}/rounds", headers=auth_headers)
        match_id = rounds_resp.json()["data"][0]["matches"][0]["id"]
        await client.patch(f"/api/v1/matches/{match_id}/result",
            json={"result": "white_win"}, headers=auth_headers)

        # Check standings
        resp = await client.get(f"/api/v1/tournaments/{t_id}/standings", headers=auth_headers)
        assert resp.status_code == 200


    async def test_full_online_game_flow(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """Full flow: tạo giải → pairing → tạo room → submit result."""
        # Setup tournament
        t_resp = await client.post("/api/v1/tournaments", json={
            "name": "Full Flow", "game_type": "chess", "time_format": "blitz",
            "format": "round_robin", "mode": "online", "max_participants": 4,
        }, headers=auth_headers)
        t_id = t_resp.json()["data"]["id"]

        me = await client.get("/api/v1/auth/me", headers=auth_headers)
        me2 = await client.get("/api/v1/auth/me", headers=second_user_headers)
        p1_id = me.json()["data"]["member_id"]
        p2_id = me2.json()["data"]["member_id"]
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": p1_id}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants",
            json={"member_id": p2_id}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/generate-pairings", headers=auth_headers)

        # Get match
        rounds_resp = await client.get(f"/api/v1/tournaments/{t_id}/rounds", headers=auth_headers)
        match_data = rounds_resp.json()["data"][0]["matches"][0]
        match_id = match_data["id"]
        assert match_data["result"] == "pending"

        # Create room from match
        room_resp = await client.post(f"/api/v1/games/from-match/{match_id}", headers=auth_headers)
        assert room_resp.status_code == 201
        room_id = room_resp.json()["data"]["id"]
        room = room_resp.json()["data"]
        assert room["status"] == "waiting"

        # Verify room has correct players
        player_ids = {room["white_player_id"], room["black_player_id"]}
        assert p1_id in player_ids
        assert p2_id in player_ids

        # Submit result (simulating game completion)
        result_resp = await client.patch(f"/api/v1/matches/{match_id}/result", json={
            "result": "white_win",
        }, headers=auth_headers)
        assert result_resp.status_code == 200

        # Verify match result updated
        rounds_resp2 = await client.get(f"/api/v1/tournaments/{t_id}/rounds", headers=auth_headers)
        updated_match = rounds_resp2.json()["data"][0]["matches"][0]
        assert updated_match["result"] == "white_win"
