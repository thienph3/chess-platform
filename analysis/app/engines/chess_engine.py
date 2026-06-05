"""Stockfish adapter cho cờ vua — sử dụng python-chess UCI protocol."""
import asyncio
from pathlib import Path

import chess
import chess.engine

from app.core.config import settings
from app.engines.base import BaseEngine, MoveClassification, PositionEvaluation, Variation


class ChessEngine(BaseEngine):
    """Wrapper cho Stockfish engine qua python-chess."""

    def __init__(self):
        self._engine: chess.engine.UciProtocol | None = None
        self._lock = asyncio.Lock()

    async def _get_engine(self) -> chess.engine.UciProtocol:
        if self._engine is None:
            transport, engine = await chess.engine.popen_uci(settings.STOCKFISH_PATH)
            self._engine = engine
        return self._engine

    async def is_available(self) -> bool:
        try:
            path = Path(settings.STOCKFISH_PATH)
            if not path.exists():
                return False
            engine = await self._get_engine()
            return engine is not None
        except Exception:
            return False

    async def analyze_position(
        self, position: str, depth: int = 20, num_variations: int = 3
    ) -> PositionEvaluation:
        async with self._lock:
            engine = await self._get_engine()
            board = chess.Board(position)

            result = await engine.analyse(
                board, chess.engine.Limit(depth=depth), multipv=num_variations
            )

            variations: list[Variation] = []
            best_move = ""
            eval_value = 0.0

            for i, info in enumerate(result if isinstance(result, list) else [result]):
                score = info.get("score")
                pv = info.get("pv", [])
                d = info.get("depth", depth)

                if score:
                    cp = score.white().score(mate_score=10000)
                    ev = cp if cp is not None else 0
                else:
                    ev = 0

                moves = [m.uci() for m in pv[:10]]
                variations.append(Variation(moves=moves, evaluation=ev, depth=d))

                if i == 0:
                    best_move = moves[0] if moves else ""
                    eval_value = ev

            return PositionEvaluation(
                eval_type="cp",
                value=eval_value,
                best_move=best_move,
                variations=variations,
                depth_reached=depth,
            )

    async def get_best_move(self, position: str, depth: int = 20) -> str:
        async with self._lock:
            engine = await self._get_engine()
            board = chess.Board(position)
            result = await engine.play(board, chess.engine.Limit(depth=depth))
            return result.move.uci() if result.move else ""

    async def review_game(self, moves: list[str], depth: int = 18) -> list[MoveClassification]:
        """Review toàn bộ ván đấu, phân loại từng nước đi."""
        async with self._lock:
            engine = await self._get_engine()
            board = chess.Board()
            classifications: list[MoveClassification] = []

            prev_eval = 0.0

            for move_uci in moves:
                # Đánh giá trước khi đi
                info_before = await engine.analyse(board, chess.engine.Limit(depth=depth))
                score_before = info_before.get("score")
                best_pv = info_before.get("pv", [])
                best_move = best_pv[0].uci() if best_pv else move_uci

                eval_before = 0.0
                if score_before:
                    cp = score_before.white().score(mate_score=10000)
                    eval_before = cp if cp is not None else 0.0

                # Thực hiện nước đi
                board.push(chess.Move.from_uci(move_uci))

                # Đánh giá sau khi đi
                info_after = await engine.analyse(board, chess.engine.Limit(depth=depth))
                score_after = info_after.get("score")
                eval_after = 0.0
                if score_after:
                    cp = score_after.white().score(mate_score=10000)
                    eval_after = cp if cp is not None else 0.0

                # Phân loại nước đi dựa trên mất mát eval
                loss = abs(eval_before - eval_after) if move_uci != best_move else 0
                classification = self._classify_move(loss, move_uci == best_move)

                classifications.append(MoveClassification(
                    move=move_uci,
                    eval_before=eval_before,
                    eval_after=eval_after,
                    best_move=best_move,
                    classification=classification,
                    depth=depth,
                ))

                prev_eval = eval_after

            return classifications

    def _classify_move(self, centipawn_loss: float, is_best: bool) -> str:
        if is_best:
            return "great"
        if centipawn_loss <= 10:
            return "good"
        if centipawn_loss <= 30:
            return "inaccuracy"
        if centipawn_loss <= 100:
            return "mistake"
        return "blunder"

    async def shutdown(self) -> None:
        if self._engine:
            await self._engine.quit()
            self._engine = None
