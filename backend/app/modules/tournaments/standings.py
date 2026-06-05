"""
Tính bảng xếp hạng giải đấu với hệ thống tiebreak.

Hỗ trợ Round Robin và Swiss:
- Điểm: thắng=1, hòa=0.5, thua=0
- Buchholz: tổng điểm của các đối thủ đã gặp
- Sonneborn-Berger: tổng điểm đối thủ * kết quả trận đấu
"""

import uuid
from dataclasses import dataclass, field

from app.modules.tournaments.models import MatchResult


@dataclass
class StandingsData:
    member_id: uuid.UUID
    points: float = 0.0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    buchholz: float = 0.0
    sonneborn_berger: float = 0.0
    rank: int = 0
    opponents: list[uuid.UUID] = field(default_factory=list)
    results_map: dict[uuid.UUID, float] = field(default_factory=dict)


def calculate_standings(
    matches: list,
    participant_ids: list[uuid.UUID],
) -> list[StandingsData]:
    """Tính bảng xếp hạng từ danh sách ván đấu và người chơi."""
    standings: dict[uuid.UUID, StandingsData] = {
        pid: StandingsData(member_id=pid) for pid in participant_ids
    }

    _accumulate_match_results(matches, standings)
    _calculate_buchholz(standings)
    _calculate_sonneborn_berger(standings)

    sorted_standings = _sort_and_rank(list(standings.values()))
    return sorted_standings


def _accumulate_match_results(
    matches: list,
    standings: dict[uuid.UUID, StandingsData],
) -> None:
    """Tích lũy kết quả từ các ván đấu đã hoàn thành."""
    for match in matches:
        if match.result == MatchResult.pending:
            continue

        white_id = match.white_player_id
        black_id = match.black_player_id

        if white_id not in standings or black_id not in standings:
            continue

        white = standings[white_id]
        black = standings[black_id]

        white.opponents.append(black_id)
        black.opponents.append(white_id)

        if match.result == MatchResult.white_win:
            white.points += 1.0
            white.wins += 1
            black.losses += 1
            white.results_map[black_id] = white.results_map.get(black_id, 0) + 1.0
            black.results_map[white_id] = black.results_map.get(white_id, 0) + 0.0
        elif match.result == MatchResult.black_win:
            black.points += 1.0
            black.wins += 1
            white.losses += 1
            black.results_map[white_id] = black.results_map.get(white_id, 0) + 1.0
            white.results_map[black_id] = white.results_map.get(black_id, 0) + 0.0
        elif match.result == MatchResult.draw:
            white.points += 0.5
            black.points += 0.5
            white.draws += 1
            black.draws += 1
            white.results_map[black_id] = white.results_map.get(black_id, 0) + 0.5
            black.results_map[white_id] = black.results_map.get(white_id, 0) + 0.5


def _calculate_buchholz(standings: dict[uuid.UUID, StandingsData]) -> None:
    """Buchholz = tổng điểm của tất cả đối thủ đã gặp."""
    for entry in standings.values():
        buchholz = 0.0
        for opp_id in entry.opponents:
            if opp_id in standings:
                buchholz += standings[opp_id].points
        entry.buchholz = buchholz


def _calculate_sonneborn_berger(standings: dict[uuid.UUID, StandingsData]) -> None:
    """Sonneborn-Berger = tổng (điểm đối thủ * kết quả trận với đối thủ đó)."""
    for entry in standings.values():
        sb = 0.0
        for opp_id, score in entry.results_map.items():
            if opp_id in standings:
                sb += standings[opp_id].points * score
        entry.sonneborn_berger = sb


def _sort_and_rank(entries: list[StandingsData]) -> list[StandingsData]:
    """Sắp xếp theo điểm > Buchholz > Sonneborn-Berger > số thắng."""
    entries.sort(
        key=lambda e: (e.points, e.buchholz, e.sonneborn_berger, e.wins),
        reverse=True,
    )
    for i, entry in enumerate(entries, start=1):
        entry.rank = i
    return entries
