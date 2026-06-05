"""Service chính điều phối phân tích cờ cho cả 3 bộ môn."""
from app.core.exceptions import AnalysisException, EngineNotAvailableException
from app.engines.base import BaseEngine, MoveClassification, PositionEvaluation
from app.engines.chess_engine import ChessEngine
from app.engines.go_engine import GoEngine
from app.engines.xiangqi_engine import XiangqiEngine

# Singleton engine instances
_chess_engine: ChessEngine | None = None
_xiangqi_engine: XiangqiEngine | None = None
_go_engine: GoEngine | None = None


def get_engine(game_type: str) -> BaseEngine:
    global _chess_engine, _xiangqi_engine, _go_engine

    if game_type == "chess":
        if _chess_engine is None:
            _chess_engine = ChessEngine()
        return _chess_engine
    elif game_type == "xiangqi":
        if _xiangqi_engine is None:
            _xiangqi_engine = XiangqiEngine()
        return _xiangqi_engine
    elif game_type == "go":
        if _go_engine is None:
            _go_engine = GoEngine()
        return _go_engine
    else:
        raise AnalysisException(f"Game type '{game_type}' không được hỗ trợ")


async def analyze_position(game_type: str, fen: str, depth: int, num_variations: int) -> PositionEvaluation:
    engine = get_engine(game_type)
    if not await engine.is_available():
        raise EngineNotAvailableException(game_type)
    return await engine.analyze_position(fen, depth, num_variations)


async def get_best_move(game_type: str, fen: str, depth: int) -> str:
    engine = get_engine(game_type)
    if not await engine.is_available():
        raise EngineNotAvailableException(game_type)
    return await engine.get_best_move(fen, depth)


async def review_game(game_type: str, moves: list[str], depth: int) -> list[MoveClassification]:
    engine = get_engine(game_type)
    if not await engine.is_available():
        raise EngineNotAvailableException(game_type)

    if game_type == "chess":
        from app.engines.chess_engine import ChessEngine
        if isinstance(engine, ChessEngine):
            return await engine.review_game(moves, depth)

    raise AnalysisException(f"Game review chưa hỗ trợ cho '{game_type}'")


async def check_engines_status() -> dict[str, bool]:
    chess_ok = await get_engine("chess").is_available() if _chess_engine else False
    xiangqi_ok = await get_engine("xiangqi").is_available() if _xiangqi_engine else False
    go_ok = await get_engine("go").is_available() if _go_engine else False
    return {"chess": chess_ok, "xiangqi": xiangqi_ok, "go": go_ok}
