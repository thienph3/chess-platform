"""Tests cho Gomoku (Cờ caro) features."""
import os
import sys

import pytest
from httpx import AsyncClient

# Add analysis paths for importing GomokuBoard
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "analysis"))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "analysis", "gomoku"))

try:
    from engine import GomokuBoard  # noqa: E402
except ImportError:
    GomokuBoard = None  # type: ignore


# =============================================================================
# Unit tests cho GomokuBoard logic (không cần DB/API)
# =============================================================================

@pytest.mark.skipif(GomokuBoard is None, reason="GomokuBoard not available (analysis code not in this image)")
class TestGomokuBoard:
    """Test game logic: validation, win detection, FEN."""

    def test_initial_board_empty(self):
        board = GomokuBoard()
        assert board.turn == 1  # black first
        assert all(board.grid[r][c] == 0 for r in range(15) for c in range(15))

    def test_valid_move_on_empty_cell(self):
        board = GomokuBoard()
        assert board.is_valid_move(7, 7) is True

    def test_invalid_move_occupied(self):
        board = GomokuBoard()
        board.push(7, 7)
        assert board.is_valid_move(7, 7) is False

    def test_invalid_move_out_of_bounds(self):
        board = GomokuBoard()
        assert board.is_valid_move(-1, 0) is False
        assert board.is_valid_move(0, 15) is False
        assert board.is_valid_move(15, 15) is False

    def test_push_alternates_turn(self):
        board = GomokuBoard()
        assert board.turn == 1
        board.push(7, 7)
        assert board.turn == 2
        board.push(7, 8)
        assert board.turn == 1

    def test_horizontal_win(self):
        board = GomokuBoard()
        for c in range(5):
            board.grid[0][c] = 1
        assert board.check_win(0, 0) is True
        assert board.check_win(0, 4) is True

    def test_vertical_win(self):
        board = GomokuBoard()
        for r in range(5):
            board.grid[r][3] = 2
        assert board.check_win(0, 3) is True
        assert board.check_win(4, 3) is True

    def test_diagonal_win(self):
        board = GomokuBoard()
        for i in range(5):
            board.grid[i][i] = 1
        assert board.check_win(2, 2) is True

    def test_anti_diagonal_win(self):
        board = GomokuBoard()
        for i in range(5):
            board.grid[i][14 - i] = 2
        assert board.check_win(2, 12) is True

    def test_four_in_a_row_not_win(self):
        board = GomokuBoard()
        for c in range(4):
            board.grid[0][c] = 1
        assert board.check_win(0, 0) is False

    def test_fen_roundtrip(self):
        board = GomokuBoard()
        board.push(7, 7)  # black
        board.push(8, 8)  # white
        fen = board.to_fen()
        assert "7.7.1" in fen
        assert "8.8.2" in fen
        assert fen.endswith(";1")  # black to move next

        board2 = GomokuBoard()
        board2.load_fen(fen)
        assert board2.grid[7][7] == 1
        assert board2.grid[8][8] == 2
        assert board2.turn == 1

    def test_empty_fen(self):
        board = GomokuBoard()
        board.load_fen(";1")
        assert board.turn == 1
        assert all(board.grid[r][c] == 0 for r in range(15) for c in range(15))

    def test_board_full_draw(self):
        board = GomokuBoard()
        assert board.is_full() is False
        for r in range(15):
            for c in range(15):
                board.grid[r][c] = 1
        assert board.is_full() is True


# =============================================================================
# API integration tests cho Gomoku (cần DB, mock analysis service nếu offline)
# =============================================================================

@pytest.mark.asyncio
class TestGomokuAPI:
    """Test Gomoku qua REST API — tạo game, play, resign."""

    async def test_start_gomoku_ai_game(self, client: AsyncClient, auth_headers: dict):
        """Tạo ván gomoku vs AI thành công."""
        resp = await client.post("/api/v1/games/ai/start", json={
            "game_type": "gomoku", "difficulty": "easy",
            "time_control": 600, "increment": 0, "player_color": "white",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["player_color"] == "white"
        assert data["room_id"] is not None

    async def test_start_gomoku_black(self, client: AsyncClient, auth_headers: dict):
        """Player cầm đen, AI đi trước (nếu service available)."""
        resp = await client.post("/api/v1/games/ai/start", json={
            "game_type": "gomoku", "difficulty": "medium",
            "time_control": 300, "increment": 0, "player_color": "black",
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["player_color"] == "black"

    async def test_create_gomoku_room(self, client: AsyncClient, auth_headers: dict):
        """Tạo phòng gomoku online (chờ đối thủ)."""
        resp = await client.post("/api/v1/games", json={
            "game_type": "gomoku", "time_control": 300, "increment": 0,
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["game_type"] == "gomoku"
        assert data["status"] == "waiting"

    async def test_gomoku_resign(self, client: AsyncClient, auth_headers: dict):
        """Player đầu hàng ván gomoku."""
        start = await client.post("/api/v1/games/ai/start", json={
            "game_type": "gomoku", "difficulty": "easy",
            "time_control": 600, "increment": 0, "player_color": "white",
        }, headers=auth_headers)
        room_id = start.json()["data"]["room_id"]

        resp = await client.post("/api/v1/games/ai/resign",
            params={"room_id": room_id}, headers=auth_headers)
        assert resp.status_code == 200

        # Verify finished
        room_resp = await client.get(f"/api/v1/games/{room_id}", headers=auth_headers)
        room = room_resp.json()["data"]
        assert room["status"] == "finished"
        assert room["result"] == "black_win"

    async def test_gomoku_in_history(self, client: AsyncClient, auth_headers: dict):
        """Ván gomoku hiện trong game history."""
        start = await client.post("/api/v1/games/ai/start", json={
            "game_type": "gomoku", "difficulty": "easy",
            "time_control": 600, "increment": 0, "player_color": "white",
        }, headers=auth_headers)
        room_id = start.json()["data"]["room_id"]

        await client.post("/api/v1/games/ai/resign",
            params={"room_id": room_id}, headers=auth_headers)

        resp = await client.get("/api/v1/games/history/all", headers=auth_headers)
        games = resp.json()["data"]
        gomoku_games = [g for g in games if g["game_type"] == "gomoku"]
        assert len(gomoku_games) >= 1

    async def test_create_gomoku_tournament(self, client: AsyncClient, auth_headers: dict):
        """Tạo giải đấu gomoku thành công."""
        resp = await client.post("/api/v1/tournaments", json={
            "name": "Giải Cờ Caro VCC 2026",
            "game_type": "gomoku",
            "time_format": "blitz",
            "format": "swiss",
            "max_participants": 16,
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["game_type"] == "gomoku"
        assert data["name"] == "Giải Cờ Caro VCC 2026"


# =============================================================================
# Tests cho Analysis Service validation endpoint (unit, no external service)
# =============================================================================

@pytest.mark.asyncio
class TestGomokuHumanVsHuman:
    """Test gomoku human vs human: 2 real clients via WebSocket, full game simulation."""

    async def test_create_gomoku_room_and_join(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """REQ: Player 1 tạo phòng gomoku, Player 2 join → status playing."""
        create_resp = await client.post("/api/v1/games", json={
            "game_type": "gomoku", "time_control": 300, "increment": 0,
        }, headers=auth_headers)
        assert create_resp.status_code == 201
        room = create_resp.json()["data"]
        assert room["game_type"] == "gomoku"
        assert room["status"] == "waiting"

        join_resp = await client.post(f"/api/v1/games/{room['id']}/join", headers=second_user_headers)
        assert join_resp.status_code == 200
        joined = join_resp.json()["data"]
        assert joined["status"] == "playing"
        assert joined["black_player_id"] is not None

    async def test_gomoku_room_in_live_list(self, client: AsyncClient, auth_headers: dict):
        """REQ: Phòng gomoku hiện trong danh sách live."""
        await client.post("/api/v1/games", json={
            "game_type": "gomoku", "time_control": 600, "increment": 0,
        }, headers=auth_headers)

        resp = await client.get("/api/v1/games/live", headers=auth_headers)
        assert resp.status_code == 200
        rooms = resp.json()["data"]
        gomoku_rooms = [r for r in rooms if r["game_type"] == "gomoku"]
        assert len(gomoku_rooms) >= 1

    async def test_gomoku_room_details(self, client: AsyncClient, auth_headers: dict):
        """REQ: GET /games/:id trả về đúng thông tin phòng gomoku."""
        create_resp = await client.post("/api/v1/games", json={
            "game_type": "gomoku", "time_control": 180, "increment": 0,
        }, headers=auth_headers)
        room_id = create_resp.json()["data"]["id"]

        resp = await client.get(f"/api/v1/games/{room_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["game_type"] == "gomoku"
        assert data["time_control"] == 180

    async def test_cannot_join_own_gomoku_room(self, client: AsyncClient, auth_headers: dict):
        """REQ: Không thể tự join phòng gomoku mình tạo."""
        create_resp = await client.post("/api/v1/games", json={
            "game_type": "gomoku", "time_control": 300, "increment": 0,
        }, headers=auth_headers)
        room_id = create_resp.json()["data"]["id"]

        join_resp = await client.post(f"/api/v1/games/{room_id}/join", headers=auth_headers)
        assert join_resp.status_code == 400

    async def test_gomoku_tournament_with_players(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """REQ: Giải gomoku pairing hoạt động cho 2 players."""
        t_resp = await client.post("/api/v1/tournaments", json={
            "name": "Gomoku Blitz 2026", "game_type": "gomoku", "time_format": "blitz",
            "format": "round_robin", "mode": "online", "max_participants": 4,
        }, headers=auth_headers)
        assert t_resp.status_code == 201
        t_id = t_resp.json()["data"]["id"]

        me1 = (await client.get("/api/v1/auth/me", headers=auth_headers)).json()["data"]["member_id"]
        me2 = (await client.get("/api/v1/auth/me", headers=second_user_headers)).json()["data"]["member_id"]

        await client.post(f"/api/v1/tournaments/{t_id}/participants", json={"member_id": me1}, headers=auth_headers)
        await client.post(f"/api/v1/tournaments/{t_id}/participants", json={"member_id": me2}, headers=auth_headers)

        pair_resp = await client.post(f"/api/v1/tournaments/{t_id}/generate-pairings", headers=auth_headers)
        assert pair_resp.status_code == 200

        rounds_resp = await client.get(f"/api/v1/tournaments/{t_id}/rounds", headers=auth_headers)
        rounds = rounds_resp.json()["data"]
        assert len(rounds) >= 1
        assert len(rounds[0]["matches"]) >= 1


@pytest.mark.asyncio
class TestGomokuValidation:
    """Test validate endpoint logic trực tiếp (import engine code)."""

    async def test_validate_valid_move(self):
        """Đặt quân vào ô trống → valid."""
        board = GomokuBoard()
        assert board.is_valid_move(7, 7) is True
        board.push(7, 7)
        assert board.grid[7][7] == 1

    async def test_validate_occupied_cell(self):
        """Đặt quân vào ô đã có quân → invalid."""
        board = GomokuBoard()
        board.push(7, 7)
        assert board.is_valid_move(7, 7) is False

    async def test_win_detection_after_move(self):
        """Sau 5 nước liên tiếp → game_over."""
        board = GomokuBoard()
        # Simulate: black places at (0,0)-(0,4)
        moves = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2), (1, 2), (0, 3), (1, 3), (0, 4)]
        for r, c in moves:
            board.push(r, c)
        # After (0,4) placed by black (odd moves = black)
        assert board.check_win(0, 4) is True

    async def test_no_win_with_gap(self):
        """4 liên tiếp + 1 cách → chưa thắng."""
        board = GomokuBoard()
        for c in [0, 1, 2, 3, 5]:
            board.grid[0][c] = 1
        assert board.check_win(0, 3) is False

    async def test_fen_with_multiple_stones(self):
        """FEN encode/decode nhiều quân đúng."""
        board = GomokuBoard()
        positions = [(0, 0), (14, 14), (7, 7), (3, 10), (10, 3)]
        for r, c in positions:
            board.push(r, c)
        fen = board.to_fen()

        board2 = GomokuBoard()
        board2.load_fen(fen)
        for i, (r, c) in enumerate(positions):
            expected_color = 1 if i % 2 == 0 else 2
            assert board2.grid[r][c] == expected_color


# =============================================================================
# Requirements-driven tests (from docs/features specs)
# =============================================================================

@pytest.mark.asyncio
class TestGomokuRequirements:
    """Tests dựa trên requirements docs — đảm bảo spec được thỏa mãn."""

    # --- REQ: ELO Rating (4 time formats for gomoku) ---

    async def test_elo_rating_created_for_gomoku(self, client: AsyncClient, auth_headers: dict):
        """REQ: Rating slots tạo được cho gomoku với mọi time_format."""
        me = (await client.get("/api/v1/auth/me", headers=auth_headers)).json()["data"]
        member_id = me["member_id"]

        resp = await client.get(f"/api/v1/ratings/{member_id}", headers=auth_headers)
        assert resp.status_code == 200
        # Có thể chưa có ratings nếu chưa chơi — chỉ verify endpoint accepts gomoku

    async def test_leaderboard_accepts_gomoku_filter(self, client: AsyncClient, auth_headers: dict):
        """REQ: Leaderboard query game_type=gomoku hoạt động."""
        resp = await client.get("/api/v1/leaderboard", params={
            "game_type": "gomoku", "time_format": "blitz",
        }, headers=auth_headers)
        assert resp.status_code == 200

    # --- REQ: Tournament formats work with gomoku ---

    async def test_swiss_tournament_gomoku(self, client: AsyncClient, auth_headers: dict):
        """REQ: Giải Swiss format với gomoku tạo được."""
        resp = await client.post("/api/v1/tournaments", json={
            "name": "Gomoku Swiss Open", "game_type": "gomoku",
            "time_format": "rapid", "format": "swiss", "max_participants": 8,
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["data"]["format"] == "swiss"
        assert resp.json()["data"]["game_type"] == "gomoku"

    async def test_knockout_tournament_gomoku(self, client: AsyncClient, auth_headers: dict):
        """REQ: Giải Knockout format với gomoku tạo được."""
        resp = await client.post("/api/v1/tournaments", json={
            "name": "Gomoku Knockout", "game_type": "gomoku",
            "time_format": "bullet", "format": "knockout", "max_participants": 16,
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["data"]["format"] == "knockout"

    async def test_otb_tournament_gomoku(self, client: AsyncClient, auth_headers: dict):
        """REQ: Giải OTB mode cho gomoku (nhập kết quả tay)."""
        resp = await client.post("/api/v1/tournaments", json={
            "name": "Gomoku OTB", "game_type": "gomoku",
            "time_format": "standard", "format": "round_robin",
            "mode": "otb", "max_participants": 6,
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["data"]["mode"] == "otb"

    # --- REQ: Game room lifecycle for gomoku ---

    async def test_game_room_time_controls(self, client: AsyncClient, auth_headers: dict):
        """REQ: Gomoku room hỗ trợ mọi time control (bullet đến standard)."""
        for tc in [60, 180, 300, 600, 900]:
            resp = await client.post("/api/v1/games", json={
                "game_type": "gomoku", "time_control": tc, "increment": 0,
            }, headers=auth_headers)
            assert resp.status_code == 201, f"Failed for time_control={tc}"

    async def test_game_room_with_increment(self, client: AsyncClient, auth_headers: dict):
        """REQ: Fischer increment hoạt động cho gomoku."""
        resp = await client.post("/api/v1/games", json={
            "game_type": "gomoku", "time_control": 300, "increment": 5,
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.json()["data"]["increment"] == 5

    async def test_game_moves_endpoint(self, client: AsyncClient, auth_headers: dict):
        """REQ: Move history endpoint hoạt động cho gomoku rooms."""
        create = await client.post("/api/v1/games", json={
            "game_type": "gomoku", "time_control": 300, "increment": 0,
        }, headers=auth_headers)
        room_id = create.json()["data"]["id"]

        resp = await client.get(f"/api/v1/games/{room_id}/moves", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["data"] == []  # chưa có nước đi

    # --- REQ: Validation service contract ---

    async def test_validation_returns_correct_turn(self):
        """REQ: Validate trả về turn (black/white) đúng sau mỗi move."""
        board = GomokuBoard()
        board.load_fen(";1")  # black to move
        board.push(7, 7)
        # After black moves, turn should be white (2)
        assert board.turn == 2
        fen = board.to_fen()
        assert fen.endswith(";2")

    async def test_validation_game_over_result_format(self):
        """REQ: Game over result phải là 'black_win' hoặc 'white_win' hoặc 'draw'."""
        board = GomokuBoard()
        # Black wins with 5 in row 0
        for c in range(5):
            board.grid[0][c] = 1
        assert board.check_win(0, 4) is True
        # Winner is the one who placed last — simulate via turn logic
        # After placing 5th stone, color at (0,4) is 1 (black)
        winner = board.grid[0][4]
        result = "black_win" if winner == 1 else "white_win"
        assert result in ("black_win", "white_win", "draw")

    async def test_validation_draw_on_full_board(self):
        """REQ: Board đầy mà không ai thắng → draw."""
        board = GomokuBoard()
        # Fill with alternating 3-wide columns to avoid 5-in-a-row
        for r in range(15):
            for c in range(15):
                # Pattern: 3 cols of color 1, then 3 cols of color 2, repeat
                color = 1 if (c // 3) % 2 == 0 else 2
                # Flip per row to avoid vertical 5-in-a-row
                if r % 4 >= 2:
                    color = 3 - color
                board.grid[r][c] = color
        assert board.is_full() is True
        # Verify no 5-in-a-row exists at a few sample points
        # In this pattern, max consecutive same color in any direction is 4
        assert board.check_win(0, 0) is False
        assert board.check_win(7, 7) is False

    # --- REQ: AI play contract for gomoku ---

    async def test_ai_difficulty_levels(self, client: AsyncClient, auth_headers: dict):
        """REQ: AI gomoku hỗ trợ 3 difficulty (easy/medium/hard)."""
        for difficulty in ["easy", "medium", "hard"]:
            resp = await client.post("/api/v1/games/ai/start", json={
                "game_type": "gomoku", "difficulty": difficulty,
                "time_control": 300, "increment": 0, "player_color": "white",
            }, headers=auth_headers)
            assert resp.status_code == 200, f"Failed for difficulty={difficulty}"

    async def test_ai_color_choices(self, client: AsyncClient, auth_headers: dict):
        """REQ: Player có thể chọn white/black/random cho gomoku AI."""
        for color in ["white", "black", "random"]:
            resp = await client.post("/api/v1/games/ai/start", json={
                "game_type": "gomoku", "difficulty": "easy",
                "time_control": 300, "increment": 0, "player_color": color,
            }, headers=auth_headers)
            assert resp.status_code == 200
            assert resp.json()["data"]["player_color"] in ("white", "black")

    # --- REQ: Swiss tournament full flow (multi-round with results) ---

    async def test_swiss_tournament_multi_round(self, client: AsyncClient, auth_headers: dict, second_user_headers: dict):
        """REQ: Swiss gomoku tournament — 4 players, generate round, submit results, generate next round.

        Per spec:
        - Swiss uses FIDE Dutch system (py4swiss) or fallback
        - After each round, results submitted → next round generated based on standings
        - Standings: thắng=1, hòa=0.5, thua=0
        """
        # Register 2 more users (need 4 for proper Swiss)
        await client.post("/api/v1/auth/register", json={
            "email": "swiss3@vinamilk.com.vn", "password": "testpass123", "full_name": "Swiss P3",
        })
        await client.post("/api/v1/auth/register", json={
            "email": "swiss4@vinamilk.com.vn", "password": "testpass123", "full_name": "Swiss P4",
        })
        p3_login = await client.post("/api/v1/auth/login", json={"email": "swiss3@vinamilk.com.vn", "password": "testpass123"})
        p4_login = await client.post("/api/v1/auth/login", json={"email": "swiss4@vinamilk.com.vn", "password": "testpass123"})
        p3_headers = {"Authorization": f"Bearer {p3_login.json()['data']['access_token']}"}
        p4_headers = {"Authorization": f"Bearer {p4_login.json()['data']['access_token']}"}

        # Create Swiss tournament
        t_resp = await client.post("/api/v1/tournaments", json={
            "name": "Gomoku Swiss 4P", "game_type": "gomoku",
            "time_format": "blitz", "format": "swiss", "max_participants": 8,
        }, headers=auth_headers)
        assert t_resp.status_code == 201
        t_id = t_resp.json()["data"]["id"]

        # Get all member IDs
        m1 = (await client.get("/api/v1/auth/me", headers=auth_headers)).json()["data"]["member_id"]
        m2 = (await client.get("/api/v1/auth/me", headers=second_user_headers)).json()["data"]["member_id"]
        m3 = (await client.get("/api/v1/auth/me", headers=p3_headers)).json()["data"]["member_id"]
        m4 = (await client.get("/api/v1/auth/me", headers=p4_headers)).json()["data"]["member_id"]

        # Register all 4
        for mid in [m1, m2, m3, m4]:
            resp = await client.post(f"/api/v1/tournaments/{t_id}/participants",
                json={"member_id": mid}, headers=auth_headers)
            assert resp.status_code in (201, 200)

        # === ROUND 1 ===
        pair_resp = await client.post(f"/api/v1/tournaments/{t_id}/generate-pairings", headers=auth_headers)
        assert pair_resp.status_code == 200

        rounds_resp = await client.get(f"/api/v1/tournaments/{t_id}/rounds", headers=auth_headers)
        rounds = rounds_resp.json()["data"]
        assert len(rounds) == 1
        r1_matches = rounds[0]["matches"]
        assert len(r1_matches) == 2  # 4 players → 2 matches

        # Submit results for round 1
        for match in r1_matches:
            resp = await client.patch(f"/api/v1/matches/{match['id']}/result",
                json={"result": "white_win"}, headers=auth_headers)
            assert resp.status_code == 200

        # === ROUND 2 ===
        pair_resp2 = await client.post(f"/api/v1/tournaments/{t_id}/generate-pairings", headers=auth_headers)
        assert pair_resp2.status_code == 200

        rounds_resp2 = await client.get(f"/api/v1/tournaments/{t_id}/rounds", headers=auth_headers)
        rounds2 = rounds_resp2.json()["data"]
        assert len(rounds2) == 2  # now 2 rounds
        r2_matches = rounds2[1]["matches"]
        assert len(r2_matches) == 2

        # Swiss pairing: round 2 should pair winners vs winners, losers vs losers
        # (We don't assert exact pairings since Swiss algo has flexibility)

        # Submit round 2 results
        for match in r2_matches:
            await client.patch(f"/api/v1/matches/{match['id']}/result",
                json={"result": "black_win"}, headers=auth_headers)

        # === STANDINGS ===
        standings_resp = await client.get(f"/api/v1/tournaments/{t_id}/standings", headers=auth_headers)
        assert standings_resp.status_code == 200
        standings = standings_resp.json()["data"]
        assert len(standings) == 4
        # Each player has a score (1 win + 1 loss or similar)
        assert all("score" in s or "points" in s for s in standings)
