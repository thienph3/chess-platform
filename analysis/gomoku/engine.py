"""Rapfi engine adapter — Gomocup protocol via async subprocess.

Board representation: 15x15 grid.
FEN format: comma-separated "row,col,color" triples + turn indicator.
  Example: "7,7,1,8,8,2;1" means black at (7,7), white at (8,8), black to move.
  Empty board: ";1" (black to move).
  Color: 1=black, 2=white.
"""
import asyncio
import os
from dataclasses import dataclass, field

from shared.base_engine import BaseEngine, PositionEvaluation, Variation

RAPFI_PATH = os.getenv("RAPFI_PATH", "/usr/local/bin/rapfi")
BOARD_SIZE = 15


@dataclass
class GomokuBoard:
    """Internal board for move validation and win detection."""

    size: int = BOARD_SIZE
    grid: list[list[int]] = field(default_factory=list)
    turn: int = 1  # 1=black, 2=white
    moves: list[tuple[int, int]] = field(default_factory=list)

    def __post_init__(self):
        if not self.grid:
            self.grid = [[0] * self.size for _ in range(self.size)]

    def load_fen(self, fen: str) -> None:
        self.grid = [[0] * self.size for _ in range(self.size)]
        self.moves = []
        if not fen or fen == ";1":
            self.turn = 1
            return
        parts = fen.split(";")
        stones = parts[0]
        self.turn = int(parts[1]) if len(parts) > 1 else 1
        if stones:
            for triple in stones.split(","):
                nums = triple.split(".")
                if len(nums) == 3:
                    r, c, color = int(nums[0]), int(nums[1]), int(nums[2])
                    self.grid[r][c] = color
                    self.moves.append((r, c))

    def to_fen(self) -> str:
        stones = []
        for r in range(self.size):
            for c in range(self.size):
                if self.grid[r][c] != 0:
                    stones.append(f"{r}.{c}.{self.grid[r][c]}")
        return f"{','.join(stones)};{self.turn}"

    def is_valid_move(self, row: int, col: int) -> bool:
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
        return self.grid[row][col] == 0

    def push(self, row: int, col: int) -> None:
        self.grid[row][col] = self.turn
        self.moves.append((row, col))
        self.turn = 3 - self.turn  # swap 1<->2

    def check_win(self, row: int, col: int) -> bool:
        """Check if placing at (row, col) resulted in 5-in-a-row."""
        color = self.grid[row][col]
        if color == 0:
            return False
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            for sign in (1, -1):
                r, c = row + dr * sign, col + dc * sign
                while 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == color:
                    count += 1
                    r += dr * sign
                    c += dc * sign
            if count >= 5:
                return True
        return False

    def is_full(self) -> bool:
        return all(self.grid[r][c] != 0 for r in range(self.size) for c in range(self.size))


class GomokuEngine(BaseEngine):
    """Rapfi engine adapter using Gomocup protocol."""

    def __init__(self):
        self._process: asyncio.subprocess.Process | None = None
        self._lock = asyncio.Lock()

    async def _start(self) -> asyncio.subprocess.Process:
        if self._process is None or self._process.returncode is not None:
            self._process = await asyncio.create_subprocess_exec(
                RAPFI_PATH,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await self._send(f"START {BOARD_SIZE}")
            resp = await self._read_response()
            if resp != "OK":
                raise RuntimeError(f"Rapfi START failed: {resp}")
            await self._send("INFO timeout_turn 3000")
        return self._process

    async def _send(self, cmd: str) -> None:
        if self._process and self._process.stdin:
            self._process.stdin.write(f"{cmd}\n".encode())
            await self._process.stdin.drain()

    async def _read_response(self, timeout: float = 5.0) -> str:
        if not self._process or not self._process.stdout:
            return ""
        try:
            deadline = asyncio.get_event_loop().time() + timeout
            while True:
                remaining = deadline - asyncio.get_event_loop().time()
                if remaining <= 0:
                    return ""
                line = await asyncio.wait_for(self._process.stdout.readline(), remaining)
                decoded = line.decode().strip()
                # Skip MESSAGE/DEBUG/LOG lines, wait for actual response
                if decoded.startswith("MESSAGE") or decoded.startswith("DEBUG") or decoded.startswith("LOG"):
                    continue
                return decoded
        except asyncio.TimeoutError:
            return ""

    async def is_available(self) -> bool:
        return os.path.exists(RAPFI_PATH)

    async def get_best_move(self, position: str, depth: int = 15) -> str:
        result = await self.analyze_position(position, depth, 1)
        return result.best_move

    async def shutdown(self) -> None:
        if self._process and self._process.returncode is None:
            self._process.terminate()
            self._process = None

    async def analyze_position(self, position: str, depth: int = 15, num_variations: int = 1) -> PositionEvaluation:
        """Get best move using Gomocup protocol."""
        async with self._lock:
            await self._start()

            board = GomokuBoard()
            board.load_fen(position)

            if not board.moves:
                # Empty board — use BEGIN
                await self._send("BEGIN")
            else:
                # Replay all moves via TURN commands (restart first)
                await self._send("RESTART")
                resp = await self._read_response(timeout=2.0)  # OK

                # Use BOARD to send full state
                await self._send("BOARD")
                for r, c in board.moves:
                    color = board.grid[r][c]
                    # Gomocup BOARD: 1=current player's stones, 2=opponent's stones
                    owner = 1 if color == board.turn else 2
                    await self._send(f"{c},{r},{owner}")
                await self._send("DONE")

            # Read response (col,row) — skips MESSAGE lines
            response = await self._read_response(timeout=5.0)
            best_move = ""
            if response and "," in response:
                parts = response.split(",")
                col, row = int(parts[0]), int(parts[1])
                best_move = f"{row},{col}"

            return PositionEvaluation(
                eval_type="cp", value=0.0, best_move=best_move,
                variations=[Variation(moves=[best_move], evaluation=0.0, depth=depth)],
                depth_reached=depth,
            )
