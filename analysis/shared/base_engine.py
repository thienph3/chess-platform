"""Abstract base class for all engine adapters."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Variation:
    moves: list[str] = field(default_factory=list)
    evaluation: float = 0.0
    depth: int = 0


@dataclass
class PositionEvaluation:
    eval_type: str = "cp"
    value: float = 0.0
    best_move: str = ""
    variations: list[Variation] = field(default_factory=list)
    depth_reached: int = 0


@dataclass
class MoveClassification:
    move: str = ""
    eval_before: float = 0.0
    eval_after: float = 0.0
    best_move: str = ""
    classification: str = "good"
    depth: int = 0


class BaseEngine(ABC):
    @abstractmethod
    async def analyze_position(self, position: str, depth: int = 20, num_variations: int = 3) -> PositionEvaluation: ...

    @abstractmethod
    async def get_best_move(self, position: str, depth: int = 20) -> str: ...

    @abstractmethod
    async def is_available(self) -> bool: ...

    @abstractmethod
    async def shutdown(self) -> None: ...
