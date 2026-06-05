"""Client gọi Analysis Service để validate moves.

Mỗi analysis service expose endpoint:
  POST /api/v1/validate
  Body: { "fen": "...", "move": "..." }
  Response: { "valid": true/false, "new_fen": "...", "game_over": false, "result": null, "reason": null }
"""
import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

ANALYSIS_URLS = {
    "chess": settings.ANALYSIS_CHESS_URL,
    "xiangqi": settings.ANALYSIS_XIANGQI_URL,
    "go": settings.ANALYSIS_GO_URL,
    "gomoku": settings.ANALYSIS_GOMOKU_URL,
}


class ValidationResult:
    def __init__(self, valid: bool, new_fen: str = "", game_over: bool = False,
                 result: str | None = None, reason: str | None = None,
                 turn: str = "", captures: dict | None = None, score: dict | None = None):
        self.valid = valid
        self.new_fen = new_fen
        self.game_over = game_over
        self.result = result
        self.reason = reason
        self.turn = turn
        self.captures = captures
        self.score = score


async def validate_move(game_type: str, fen: str, move: dict[str, Any]) -> ValidationResult:
    """Gọi analysis service để validate nước đi.

    Args:
        game_type: "chess", "xiangqi", "go"
        fen: Trạng thái hiện tại của bàn cờ
        move: Dict chứa thông tin nước đi (format tùy game type)

    Returns:
        ValidationResult
    """
    base_url = ANALYSIS_URLS.get(game_type)
    if not base_url:
        return ValidationResult(valid=False)

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{base_url}/api/v1/validate",
                json={"fen": fen, "move": move},
            )

        if response.status_code != 200:
            logger.warning("Validation service returned %d for %s", response.status_code, game_type)
            return ValidationResult(valid=False)

        data = response.json()
        return ValidationResult(
            valid=data.get("valid", False),
            new_fen=data.get("new_fen", ""),
            game_over=data.get("game_over", False),
            result=data.get("result"),
            reason=data.get("reason"),
            turn=data.get("turn", ""),
            captures=data.get("captures"),
            score=data.get("score"),
        )

    except httpx.TimeoutException:
        logger.error("Validation service timeout for %s", game_type)
        return ValidationResult(valid=False)
    except Exception as exc:
        logger.error("Validation service error for %s: %s", game_type, exc)
        return ValidationResult(valid=False)


async def get_initial_state(game_type: str) -> dict[str, Any]:
    """Lấy trạng thái ban đầu từ analysis service."""
    base_url = ANALYSIS_URLS.get(game_type)
    if not base_url:
        return {"fen": "", "turn": "white", "game_over": False}

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}/api/v1/initial-state")

        if response.status_code == 200:
            return response.json()
    except Exception as exc:
        logger.error("Failed to get initial state for %s: %s", game_type, exc)

    # Fallback defaults
    defaults = {
        "chess": {"fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", "turn": "white"},
        "xiangqi": {"fen": "rheakaehr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RHEAKAEHR w - - 0 1", "turn": "red"},
        "go": {"fen": "", "turn": "black"},
        "gomoku": {"fen": "", "turn": "black"},
    }
    return {**defaults.get(game_type, {}), "game_over": False}
