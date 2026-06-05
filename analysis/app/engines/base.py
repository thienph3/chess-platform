"""Abstract base class for all engine adapters."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Variation:
    moves: list[str]
    evaluation: float  # centipawns hoặc win%
    depth: int


@dataclass
class PositionEvaluation:
    eval_type: str  # "cp" (centipawns) hoặc "winrate"
    value: float
    best_move: str
    variations: list[Variation]
    depth_reached: int


@dataclass
class MoveClassification:
    move: str
    eval_before: float
    eval_after: float
    best_move: str
    classification: str  # brilliant, great, good, inaccuracy, mistake, blunder
    depth: int


class BaseEngine(ABC):
    """Interface chung cho tất cả engine adapters."""

    @abstractmethod
    async def analyze_position(
        self, position: str, depth: int = 20, num_variations: int = 3
    ) -> PositionEvaluation:
        """Đánh giá 1 thế cờ."""
        ...

    @abstractmethod
    async def get_best_move(self, position: str, depth: int = 20) -> str:
        """Trả về nước đi tốt nhất."""
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        """Kiểm tra engine có sẵn sàng không."""
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        """Tắt engine process."""
        ...
