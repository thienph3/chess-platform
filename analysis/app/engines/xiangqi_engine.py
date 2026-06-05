"""Pikafish/Fairy-Stockfish adapter cho cờ tướng — UCI protocol."""
import asyncio
from pathlib import Path

from app.core.config import settings
from app.engines.base import BaseEngine, PositionEvaluation, Variation


class XiangqiEngine(BaseEngine):
    """
    Wrapper cho Pikafish (Xiangqi engine).
    Pikafish sử dụng UCI protocol tương tự Stockfish nhưng cho cờ tướng.
    FEN format cho Xiangqi: "rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1"
    """

    def __init__(self):
        self._process: asyncio.subprocess.Process | None = None
        self._lock = asyncio.Lock()

    async def _start_engine(self) -> asyncio.subprocess.Process:
        if self._process is None or self._process.returncode is not None:
            self._process = await asyncio.create_subprocess_exec(
                settings.PIKAFISH_PATH,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await self._send_command("uci")
            await self._wait_for("uciok")
            await self._send_command("isready")
            await self._wait_for("readyok")
        return self._process

    async def _send_command(self, cmd: str) -> None:
        if self._process and self._process.stdin:
            self._process.stdin.write(f"{cmd}\n".encode())
            await self._process.stdin.drain()

    async def _wait_for(self, token: str, timeout: float = 10.0) -> list[str]:
        lines: list[str] = []
        if not self._process or not self._process.stdout:
            return lines
        try:
            while True:
                line = await asyncio.wait_for(self._process.stdout.readline(), timeout)
                decoded = line.decode().strip()
                lines.append(decoded)
                if token in decoded:
                    break
        except asyncio.TimeoutError:
            pass
        return lines

    async def is_available(self) -> bool:
        path = Path(settings.PIKAFISH_PATH)
        return path.exists()

    async def analyze_position(
        self, position: str, depth: int = 20, num_variations: int = 3
    ) -> PositionEvaluation:
        async with self._lock:
            await self._start_engine()
            await self._send_command(f"setoption name MultiPV value {num_variations}")
            await self._send_command(f"position fen {position}")
            await self._send_command(f"go depth {depth}")
            lines = await self._wait_for("bestmove", timeout=settings.ENGINE_TIMEOUT)

            variations: list[Variation] = []
            best_move = ""
            eval_value = 0.0

            for line in lines:
                if line.startswith("info") and "score" in line and "pv" in line:
                    ev = self._parse_score(line)
                    moves = self._parse_pv(line)
                    d = self._parse_depth(line)
                    variations.append(Variation(moves=moves, evaluation=ev, depth=d))

                if line.startswith("bestmove"):
                    parts = line.split()
                    if len(parts) >= 2:
                        best_move = parts[1]

            if variations:
                eval_value = variations[0].evaluation

            return PositionEvaluation(
                eval_type="cp", value=eval_value, best_move=best_move,
                variations=variations[:num_variations], depth_reached=depth,
            )

    async def get_best_move(self, position: str, depth: int = 20) -> str:
        result = await self.analyze_position(position, depth, 1)
        return result.best_move

    def _parse_score(self, line: str) -> float:
        parts = line.split()
        try:
            idx = parts.index("score")
            if parts[idx + 1] == "cp":
                return float(parts[idx + 2])
            elif parts[idx + 1] == "mate":
                return 10000.0 if float(parts[idx + 2]) > 0 else -10000.0
        except (ValueError, IndexError):
            pass
        return 0.0

    def _parse_pv(self, line: str) -> list[str]:
        parts = line.split()
        try:
            idx = parts.index("pv")
            return parts[idx + 1:]
        except ValueError:
            return []

    def _parse_depth(self, line: str) -> int:
        parts = line.split()
        try:
            idx = parts.index("depth")
            return int(parts[idx + 1])
        except (ValueError, IndexError):
            return 0

    async def shutdown(self) -> None:
        if self._process:
            await self._send_command("quit")
            self._process = None
