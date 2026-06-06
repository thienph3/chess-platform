"""E2E tests against live deployment.

Run: python -m pytest tests/test_e2e_live.py -v
"""
import pytest
import httpx

BASE_URL = "http://dev-ml.tech.vinamilklocal.com/chess/api"


@pytest.fixture(scope="module")
def api():
    return httpx.Client(base_url=BASE_URL, timeout=15)


@pytest.fixture(scope="module")
def token1(api):
    api.post("/v1/auth/register", json={"email": "e2e1@vinamilk.com.vn", "password": "123456", "full_name": "P1"})
    r = api.post("/v1/auth/login", json={"email": "e2e1@vinamilk.com.vn", "password": "123456"})
    return r.json()["data"]["access_token"]


@pytest.fixture(scope="module")
def token2(api):
    api.post("/v1/auth/register", json={"email": "e2e2@vinamilk.com.vn", "password": "123456", "full_name": "P2"})
    r = api.post("/v1/auth/login", json={"email": "e2e2@vinamilk.com.vn", "password": "123456"})
    return r.json()["data"]["access_token"]


def h(token):
    return {"Authorization": f"Bearer {token}"}


class TestGomokuVsAI:
    """Human vs AI on live deployment."""

    def test_start_and_play_move(self, api, token1):
        """Player starts game, places a stone, gets valid response."""
        start = api.post("/v1/games/ai/start", json={
            "game_type": "gomoku", "difficulty": "easy",
            "time_control": 300, "increment": 0, "player_color": "white",
        }, headers=h(token1)).json()["data"]
        assert start["room_id"]
        assert start["fen"] == ";1"

        play = api.post("/v1/games/ai/play", json={
            "room_id": start["room_id"], "move": {"row": 7, "col": 7}
        }, headers=h(token1)).json()["data"]
        assert play["valid"] is True
        assert "7.7" in play["new_fen"]

    def test_ai_responds(self, api, token1):
        """After player moves, AI must respond with a move."""
        room_id = api.post("/v1/games/ai/start", json={
            "game_type": "gomoku", "difficulty": "easy",
            "time_control": 300, "increment": 0, "player_color": "white",
        }, headers=h(token1)).json()["data"]["room_id"]

        play = api.post("/v1/games/ai/play", json={
            "room_id": room_id, "move": {"row": 7, "col": 7}
        }, headers=h(token1)).json()["data"]
        assert play["valid"] is True
        assert play["ai_move"] is not None, "AI did not respond"
        assert play["ai_move"] != "", "AI move should not be empty"

    def test_player_can_play_multiple_turns(self, api, token1):
        """Player and AI alternate — player can make 3 moves."""
        room_id = api.post("/v1/games/ai/start", json={
            "game_type": "gomoku", "difficulty": "easy",
            "time_control": 300, "increment": 0, "player_color": "white",
        }, headers=h(token1)).json()["data"]["room_id"]

        for row, col in [(7, 7), (5, 5), (3, 3)]:
            play = api.post("/v1/games/ai/play", json={
                "room_id": room_id, "move": {"row": row, "col": col}
            }, headers=h(token1)).json()["data"]
            assert play["valid"] is True, f"Move ({row},{col}) rejected: {play}"

    def test_invalid_move_on_occupied(self, api, token1):
        """Placing on occupied cell → valid=False."""
        room_id = api.post("/v1/games/ai/start", json={
            "game_type": "gomoku", "difficulty": "easy",
            "time_control": 300, "increment": 0, "player_color": "white",
        }, headers=h(token1)).json()["data"]["room_id"]

        api.post("/v1/games/ai/play", json={
            "room_id": room_id, "move": {"row": 7, "col": 7}
        }, headers=h(token1))

        play = api.post("/v1/games/ai/play", json={
            "room_id": room_id, "move": {"row": 7, "col": 7}
        }, headers=h(token1)).json()["data"]
        assert play["valid"] is False

    def test_resign(self, api, token1):
        """Player resigns → game finished."""
        room_id = api.post("/v1/games/ai/start", json={
            "game_type": "gomoku", "difficulty": "easy",
            "time_control": 300, "increment": 0, "player_color": "white",
        }, headers=h(token1)).json()["data"]["room_id"]

        api.post("/v1/games/ai/resign", params={"room_id": room_id}, headers=h(token1))
        room = api.get(f"/v1/games/{room_id}", headers=h(token1)).json()["data"]
        assert room["status"] == "finished"


class TestGomokuHumanVsHuman:
    """Two players on live deployment."""

    def test_create_join_room(self, api, token1, token2):
        """P1 creates, P2 joins → status playing."""
        room = api.post("/v1/games", json={
            "game_type": "gomoku", "time_control": 300, "increment": 0,
        }, headers=h(token1)).json()["data"]
        assert room["status"] == "waiting"

        joined = api.post(f"/v1/games/{room['id']}/join", headers=h(token2)).json()["data"]
        assert joined["status"] == "playing"
        assert joined["black_player_id"] is not None

    def test_cannot_join_own_room(self, api, token1):
        """Cannot self-join."""
        room_id = api.post("/v1/games", json={
            "game_type": "gomoku", "time_control": 300, "increment": 0,
        }, headers=h(token1)).json()["data"]["id"]

        r = api.post(f"/v1/games/{room_id}/join", headers=h(token1))
        assert r.status_code == 400

    def test_room_in_live_list(self, api, token1):
        """Gomoku room appears in live list."""
        api.post("/v1/games", json={
            "game_type": "gomoku", "time_control": 300, "increment": 0,
        }, headers=h(token1))

        rooms = api.get("/v1/games/live", headers=h(token1)).json()["data"]
        assert any(r["game_type"] == "gomoku" for r in rooms)

    def test_tournament_pairing(self, api, token1, token2):
        """Swiss tournament: create, register 2, pair."""
        t_id = api.post("/v1/tournaments", json={
            "name": "E2E Swiss", "game_type": "gomoku",
            "time_format": "blitz", "format": "swiss", "max_participants": 8,
        }, headers=h(token1)).json()["data"]["id"]

        m1 = api.get("/v1/auth/me", headers=h(token1)).json()["data"]["member_id"]
        m2 = api.get("/v1/auth/me", headers=h(token2)).json()["data"]["member_id"]
        api.post(f"/v1/tournaments/{t_id}/participants", json={"member_id": m1}, headers=h(token1))
        api.post(f"/v1/tournaments/{t_id}/participants", json={"member_id": m2}, headers=h(token1))

        pair = api.post(f"/v1/tournaments/{t_id}/generate-pairings", headers=h(token1))
        assert pair.status_code == 200
        rounds = api.get(f"/v1/tournaments/{t_id}/rounds", headers=h(token1)).json()["data"]
        assert len(rounds[0]["matches"]) >= 1
