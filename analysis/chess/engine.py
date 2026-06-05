"""Stockfish engine adapter using python-chess."""
import asyncio
import os

import chess
import chess.engine
import chess.polyglot

from shared.base_engine import BaseEngine, MoveClassification, PositionEvaluation, Variation

STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", "/usr/games/stockfish")


class ChessEngine(BaseEngine):
    def __init__(self):
        self._engine: chess.engine.UciProtocol | None = None
        self._lock = asyncio.Lock()

    async def _get_engine(self) -> chess.engine.UciProtocol:
        if self._engine is None:
            _, engine = await chess.engine.popen_uci(STOCKFISH_PATH)
            self._engine = engine
        return self._engine

    async def is_available(self) -> bool:
        try:
            engine = await self._get_engine()
            return engine is not None
        except Exception:
            return False

    async def analyze_position(self, position: str, depth: int = 20, num_variations: int = 3) -> PositionEvaluation:
        async with self._lock:
            engine = await self._get_engine()
            board = chess.Board(position)
            result = await engine.analyse(board, chess.engine.Limit(depth=depth), multipv=num_variations)

            variations: list[Variation] = []
            best_move = ""
            eval_value = 0.0

            for i, info in enumerate(result if isinstance(result, list) else [result]):
                score = info.get("score")
                pv = info.get("pv", [])
                d = info.get("depth", depth)
                ev = score.white().score(mate_score=10000) if score else 0
                moves = [m.uci() for m in pv[:10]]
                variations.append(Variation(moves=moves, evaluation=ev or 0, depth=d))
                if i == 0:
                    best_move = moves[0] if moves else ""
                    eval_value = ev or 0

            return PositionEvaluation(eval_type="cp", value=eval_value, best_move=best_move, variations=variations, depth_reached=depth)

    async def get_best_move(self, position: str, depth: int = 20) -> str:
        async with self._lock:
            engine = await self._get_engine()
            board = chess.Board(position)
            result = await engine.play(board, chess.engine.Limit(depth=depth))
            return result.move.uci() if result.move else ""

    async def review_game(self, moves: list[str], depth: int = 18) -> list[MoveClassification]:
        async with self._lock:
            engine = await self._get_engine()
            board = chess.Board()
            classifications: list[MoveClassification] = []

            # Load opening book
            book_reader = None
            try:
                import os
                book_path = os.getenv("BOOK_PATH", "/app/book.bin")
                if os.path.exists(book_path):
                    book_reader = chess.polyglot.open_reader(book_path)
            except Exception:
                pass

            for move_uci in moves:
                # Check if position is in opening book
                is_book = False
                if book_reader:
                    try:
                        entry = book_reader.get(board)
                        if entry is not None:
                            is_book = True
                    except Exception:
                        pass

                if is_book:
                    # Book move — skip engine analysis
                    board.push(chess.Move.from_uci(move_uci))
                    classifications.append(MoveClassification(
                        move=move_uci, eval_before=0, eval_after=0,
                        best_move=move_uci, classification="book", depth=0,
                    ))
                    continue

                info_before = await engine.analyse(board, chess.engine.Limit(depth=depth))
                score_before = info_before.get("score")
                best_pv = info_before.get("pv", [])
                best_move = best_pv[0].uci() if best_pv else move_uci
                eval_before = score_before.white().score(mate_score=10000) if score_before else 0

                board.push(chess.Move.from_uci(move_uci))

                info_after = await engine.analyse(board, chess.engine.Limit(depth=depth))
                score_after = info_after.get("score")
                eval_after = score_after.white().score(mate_score=10000) if score_after else 0

                loss = abs((eval_before or 0) - (eval_after or 0)) if move_uci != best_move else 0
                classification = (
                    "brilliant" if move_uci == best_move and loss == 0 and abs(eval_after or 0) > 100 else
                    "great" if move_uci == best_move else
                    "good" if loss <= 20 else
                    "inaccuracy" if loss <= 50 else
                    "mistake" if loss <= 150 else
                    "blunder"
                )

                classifications.append(MoveClassification(
                    move=move_uci, eval_before=eval_before or 0, eval_after=eval_after or 0,
                    best_move=best_move, classification=classification, depth=depth,
                ))
            return classifications

    async def shutdown(self) -> None:
        if self._engine:
            await self._engine.quit()
            self._engine = None
