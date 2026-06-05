"""KataGo adapter cho cờ vây — GTP protocol."""
import asyncio
from pathlib import Path

from app.core.config import settings
from app.engines.base import BaseEngine, PositionEvaluation, Variation


class GoEngine(BaseEngine):
    """
    Wrapper cho KataGo (Go engine).
    KataGo sử dụng GTP (Go Text Protocol) hoặc analysis mode.
    Position format: SGF hoặc list of moves.
    """

    def __init__(self):
        self._process: asyncio.subprocess.Process | None = None
        self._lock = asyncio.Lock()

    async def _start_engine(self) -> asyncio.subprocess.Process:
        if self._process is None or self._process.returncode is not None:
            self._process = await asyncio.create_subprocess_exec(
                settings.KATAGO_PATH, "gtp",
                "-model", settings.KATAGO_MODEL_PATH,
                "-config", settings.KATAGO_CONFIG_PATH,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            # Wait for GTP ready
            await self._send_gtp("name")
            await self._read_gtp_response()
        return self._process

    async def _send_gtp(self, cmd: str) -> None:
        if self._process and self._process.stdin:
            self._process.stdin.write(f"{cmd}\n".encode())
            await self._process.stdin.drain()

    async def _read_gtp_response(self, timeout: float = 30.0) -> str:
        if not self._process or not self._process.stdout:
            return ""
        lines: list[str] = []
        try:
            while True:
                line = await asyncio.wait_for(self._process.stdout.readline(), timeout)
                decoded = line.decode().strip()
                if decoded == "" and lines:
                    break
                lines.append(decoded)
        except asyncio.TimeoutError:
            pass
        return "\n".join(lines)

    async def is_available(self) -> bool:
        katago = Path(settings.KATAGO_PATH)
        model = Path(settings.KATAGO_MODEL_PATH)
        return katago.exists() and model.exists()

    async def analyze_position(
        self, position: str, depth: int = 20, num_variations: int = 3
    ) -> PositionEvaluation:
        """
        Cho Go, 'position' là chuỗi moves hoặc board state.
        'depth' map sang số visits cho KataGo.
        """
        async with self._lock:
            await self._start_engine()

            # Clear board
            await self._send_gtp("clear_board")
            await self._read_gtp_response()

            # Set board size (default 19x19)
            await self._send_gtp("boardsize 19")
            await self._read_gtp_response()

            # Play moves if position contains them
            if position and position != "empty":
                moves = position.split()
                color = "B"
                for move in moves:
                    await self._send_gtp(f"play {color} {move}")
                    await self._read_gtp_response()
                    color = "W" if color == "B" else "B"

            # Get best move
            await self._send_gtp("genmove B")
            response = await self._read_gtp_response()
            best_move = response.replace("= ", "").strip()

            # KataGo doesn't easily give eval in GTP mode
            # For full analysis, use KataGo analysis mode (JSON) in future
            return PositionEvaluation(
                eval_type="winrate",
                value=50.0,  # placeholder — cần analysis mode cho winrate thực
                best_move=best_move,
                variations=[Variation(moves=[best_move], evaluation=50.0, depth=depth)],
                depth_reached=depth,
            )

    async def get_best_move(self, position: str, depth: int = 20) -> str:
        result = await self.analyze_position(position, depth, 1)
        return result.best_move

    async def shutdown(self) -> None:
        if self._process:
            await self._send_gtp("quit")
            self._process = None
