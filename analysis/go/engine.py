"""KataGo engine adapter — GTP protocol via async subprocess."""
import asyncio
import os

from shared.base_engine import BaseEngine, PositionEvaluation, Variation

KATAGO_PATH = os.getenv("KATAGO_PATH", "/usr/local/bin/katago")
KATAGO_MODEL = os.getenv("KATAGO_MODEL_PATH", "/usr/local/share/katago/model.bin.gz")
KATAGO_CONFIG = os.getenv("KATAGO_CONFIG_PATH", "/usr/local/share/katago/config.cfg")


class GoEngine(BaseEngine):
    def __init__(self):
        self._process: asyncio.subprocess.Process | None = None
        self._lock = asyncio.Lock()

    async def _start(self) -> asyncio.subprocess.Process:
        if self._process is None or self._process.returncode is not None:
            self._process = await asyncio.create_subprocess_exec(
                KATAGO_PATH, "gtp", "-model", KATAGO_MODEL, "-config", KATAGO_CONFIG,
                stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await self._gtp("name")
            await self._read_response()
        return self._process

    async def _gtp(self, cmd: str) -> None:
        if self._process and self._process.stdin:
            self._process.stdin.write(f"{cmd}\n".encode())
            await self._process.stdin.drain()

    async def _read_response(self, timeout: float = 30.0) -> str:
        if not self._process or not self._process.stdout:
            return ""
        lines: list[str] = []
        try:
            while True:
                line = await asyncio.wait_for(self._process.stdout.readline(), timeout)
                decoded = line.decode().strip()
                if decoded == "" and lines:
                    break
                if decoded:
                    lines.append(decoded)
        except asyncio.TimeoutError:
            pass
        return "\n".join(lines)

    async def is_available(self) -> bool:
        return os.path.exists(KATAGO_PATH) and os.path.exists(KATAGO_MODEL)

    async def analyze_position(self, position: str, depth: int = 20, num_variations: int = 3) -> PositionEvaluation:
        """position = space-separated moves (e.g. "D4 Q16 C17") or "empty" for new game."""
        async with self._lock:
            await self._start()
            await self._gtp("clear_board")
            await self._read_response()
            await self._gtp("boardsize 19")
            await self._read_response()

            # Play moves
            if position and position != "empty":
                moves = position.split()
                color = "B"
                for move in moves:
                    await self._gtp(f"play {color} {move}")
                    await self._read_response()
                    color = "W" if color == "B" else "B"
                next_color = color
            else:
                next_color = "B"

            # Generate best move
            await self._gtp(f"genmove {next_color}")
            response = await self._read_response()
            best_move = response.replace("=", "").strip()

            # Undo the generated move
            await self._gtp("undo")
            await self._read_response()

            return PositionEvaluation(
                eval_type="winrate", value=50.0,
                best_move=best_move,
                variations=[Variation(moves=[best_move], evaluation=50.0, depth=depth)],
                depth_reached=depth,
            )

    async def get_best_move(self, position: str, depth: int = 20) -> str:
        result = await self.analyze_position(position, depth, 1)
        return result.best_move

    async def shutdown(self) -> None:
        if self._process:
            await self._gtp("quit")
            self._process = None


# --- GoBoard for move validation (ko rule, suicide prevention) ---

EMPTY = 0
BLACK = 1
WHITE = 2


class GoBoard:
    """Go board with move validation."""

    def __init__(self, size: int = 19):
        self.size = size
        self.board: list[list[int]] = [[EMPTY] * size for _ in range(size)]
        self.turn = BLACK
        self.ko_point: tuple[int, int] | None = None
        self.passes = 0
        self.captures = {BLACK: 0, WHITE: 0}

    def load_fen(self, fen: str) -> None:
        """Parse simple FEN: rows/rows turn move_count."""
        parts = fen.split(" ")
        rows = parts[0].split("/")
        for r, row_str in enumerate(rows):
            col = 0
            for ch in row_str:
                if ch.isdigit():
                    col += int(ch)
                elif ch == "B":
                    self.board[r][col] = BLACK
                    col += 1
                elif ch == "W":
                    self.board[r][col] = WHITE
                    col += 1
        if len(parts) > 1:
            self.turn = BLACK if parts[1] == "b" else WHITE

    def to_fen(self) -> str:
        rows = []
        for r in range(self.size):
            row_str = ""
            empty = 0
            for c in range(self.size):
                if self.board[r][c] == EMPTY:
                    empty += 1
                else:
                    if empty:
                        row_str += str(empty)
                        empty = 0
                    row_str += "B" if self.board[r][c] == BLACK else "W"
            if empty:
                row_str += str(empty)
            rows.append(row_str)
        turn_str = "b" if self.turn == BLACK else "w"
        return "/".join(rows) + f" {turn_str} 0"

    def _neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        result = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.size and 0 <= nc < self.size:
                result.append((nr, nc))
        return result

    def _get_group(self, r: int, c: int) -> tuple[set, set]:
        color = self.board[r][c]
        group: set[tuple[int, int]] = set()
        liberties: set[tuple[int, int]] = set()
        stack = [(r, c)]
        while stack:
            cr, cc = stack.pop()
            if (cr, cc) in group:
                continue
            group.add((cr, cc))
            for nr, nc in self._neighbors(cr, cc):
                if self.board[nr][nc] == EMPTY:
                    liberties.add((nr, nc))
                elif self.board[nr][nc] == color and (nr, nc) not in group:
                    stack.append((nr, nc))
        return group, liberties

    def is_valid_move(self, r: int, c: int) -> bool:
        if not (0 <= r < self.size and 0 <= c < self.size):
            return False
        if self.board[r][c] != EMPTY:
            return False
        if (r, c) == self.ko_point:
            return False

        self.board[r][c] = self.turn
        opponent = WHITE if self.turn == BLACK else BLACK
        has_capture = False
        for nr, nc in self._neighbors(r, c):
            if self.board[nr][nc] == opponent:
                _, libs = self._get_group(nr, nc)
                if not libs:
                    has_capture = True
                    break

        if not has_capture:
            _, own_libs = self._get_group(r, c)
            if not own_libs:
                self.board[r][c] = EMPTY
                return False

        self.board[r][c] = EMPTY
        return True

    def push(self, r: int, c: int) -> bool:
        if not self.is_valid_move(r, c):
            return False
        self.board[r][c] = self.turn
        opponent = WHITE if self.turn == BLACK else BLACK
        total_captured = 0
        captured_single = None

        for nr, nc in self._neighbors(r, c):
            if self.board[nr][nc] == opponent:
                group, libs = self._get_group(nr, nc)
                if not libs:
                    total_captured += len(group)
                    if len(group) == 1:
                        captured_single = list(group)[0]
                    for gr, gc in group:
                        self.board[gr][gc] = EMPTY

        self.captures[self.turn] = self.captures.get(self.turn, 0) + total_captured

        if total_captured == 1 and captured_single:
            _, own_libs = self._get_group(r, c)
            self.ko_point = captured_single if len(own_libs) == 1 else None
        else:
            self.ko_point = None

        self.turn = opponent
        self.passes = 0
        return True

    def pass_turn(self) -> None:
        self.turn = WHITE if self.turn == BLACK else BLACK
        self.passes += 1
        self.ko_point = None

    def is_game_over(self) -> bool:
        return self.passes >= 2

    def score(self, komi: float = 6.5) -> dict:
        territory = {BLACK: 0, WHITE: 0}
        visited: set = set()
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] != EMPTY or (r, c) in visited:
                    continue
                region: set = set()
                borders: set = set()
                stack = [(r, c)]
                while stack:
                    cr, cc = stack.pop()
                    if (cr, cc) in region:
                        continue
                    region.add((cr, cc))
                    visited.add((cr, cc))
                    for nr, nc in self._neighbors(cr, cc):
                        if self.board[nr][nc] == EMPTY and (nr, nc) not in region:
                            stack.append((nr, nc))
                        elif self.board[nr][nc] != EMPTY:
                            borders.add(self.board[nr][nc])
                if len(borders) == 1:
                    territory[list(borders)[0]] += len(region)

        stones = {BLACK: 0, WHITE: 0}
        for r in range(self.size):
            for c in range(self.size):
                if self.board[r][c] != EMPTY:
                    stones[self.board[r][c]] += 1

        b = stones[BLACK] + territory[BLACK]
        w = stones[WHITE] + territory[WHITE] + komi
        return {"black": b, "white": w, "winner": "black" if b > w else "white"}
