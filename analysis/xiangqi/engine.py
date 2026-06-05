"""Pikafish engine adapter — UCI protocol via async subprocess."""
import asyncio
import os

from shared.base_engine import BaseEngine, PositionEvaluation, Variation

PIKAFISH_PATH = os.getenv("PIKAFISH_PATH", "/usr/local/bin/pikafish")


class XiangqiEngine(BaseEngine):
    def __init__(self):
        self._process: asyncio.subprocess.Process | None = None
        self._lock = asyncio.Lock()

    async def _start(self) -> asyncio.subprocess.Process:
        if self._process is None or self._process.returncode is not None:
            self._process = await asyncio.create_subprocess_exec(
                PIKAFISH_PATH,
                stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await self._cmd("uci")
            await self._wait("uciok")
            await self._cmd("isready")
            await self._wait("readyok")
        return self._process

    async def _cmd(self, cmd: str) -> None:
        if self._process and self._process.stdin:
            self._process.stdin.write(f"{cmd}\n".encode())
            await self._process.stdin.drain()

    async def _wait(self, token: str, timeout: float = 30.0) -> list[str]:
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
        return os.path.exists(PIKAFISH_PATH)

    async def analyze_position(self, position: str, depth: int = 20, num_variations: int = 3) -> PositionEvaluation:
        async with self._lock:
            await self._start()
            await self._cmd(f"setoption name MultiPV value {num_variations}")
            await self._cmd(f"position fen {position}")
            await self._cmd(f"go depth {depth}")
            lines = await self._wait("bestmove", timeout=30.0)

            variations: list[Variation] = []
            best_move = ""

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

            eval_value = variations[0].evaluation if variations else 0.0
            return PositionEvaluation(eval_type="cp", value=eval_value, best_move=best_move, variations=variations[:num_variations], depth_reached=depth)

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
            return parts[parts.index("pv") + 1:]
        except ValueError:
            return []

    def _parse_depth(self, line: str) -> int:
        parts = line.split()
        try:
            return int(parts[parts.index("depth") + 1])
        except (ValueError, IndexError):
            return 0

    async def shutdown(self) -> None:
        if self._process:
            await self._cmd("quit")
            self._process = None

    async def validate_move(self, fen: str, uci_move: str) -> tuple[bool, str, dict]:
        """
        Validate move bằng Pikafish: position fen ... moves <move>, rồi check legality.
        Returns: (is_valid, new_fen, game_over_info)
        """
        async with self._lock:
            await self._start()

            # Set position và thử move
            await self._cmd(f"position fen {fen} moves {uci_move}")
            await self._cmd("d")  # display board — Pikafish outputs FEN
            lines = await self._wait("Checkers:", timeout=5.0)

            # Parse FEN từ output
            new_fen = ""
            for line in lines:
                if line.startswith("Fen:"):
                    new_fen = line[4:].strip()
                    break

            if not new_fen:
                # Move was illegal — Pikafish sẽ không output FEN hợp lệ
                return (False, "", {})

            # Check game over: thử generate move, nếu không có → game over
            await self._cmd(f"position fen {new_fen}")
            await self._cmd("go depth 1")
            go_lines = await self._wait("bestmove", timeout=5.0)

            game_over_info: dict = {"game_over": False}
            for line in go_lines:
                if "bestmove (none)" in line or "bestmove 0000" in line:
                    game_over_info["game_over"] = True
                    # Determine if checkmate or stalemate
                    # Nếu có "score mate 0" → checkmate
                    for info_line in go_lines:
                        if "score mate 0" in info_line:
                            parts = new_fen.split()
                            loser_turn = parts[1] if len(parts) > 1 else "w"
                            game_over_info["result"] = "black_win" if loser_turn == "w" else "red_win"
                            game_over_info["reason"] = "checkmate"
                            break
                    if "reason" not in game_over_info:
                        game_over_info["result"] = "draw"
                        game_over_info["reason"] = "stalemate"

            return (True, new_fen, game_over_info)
