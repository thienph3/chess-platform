"""Pairing generation logic for different tournament formats."""
import random
import uuid

from app.modules.tournaments.models import Match, MatchResult


def generate_round_robin_pairings(player_ids: list[uuid.UUID]) -> list[list[tuple[uuid.UUID, uuid.UUID]]]:
    """
    Tạo tất cả cặp đấu cho Round Robin.
    Trả về danh sách các vòng, mỗi vòng là list các cặp (white, black).
    """
    players = list(player_ids)
    if len(players) % 2 != 0:
        players.append(None)  # type: ignore

    n = len(players)
    rounds: list[list[tuple[uuid.UUID, uuid.UUID]]] = []

    for round_idx in range(n - 1):
        round_pairings: list[tuple[uuid.UUID, uuid.UUID]] = []
        for i in range(n // 2):
            p1 = players[i]
            p2 = players[n - 1 - i]
            if p1 is None or p2 is None:
                continue
            # Xen kẽ trắng/đen theo vòng
            if round_idx % 2 == 0:
                round_pairings.append((p1, p2))
            else:
                round_pairings.append((p2, p1))
        rounds.append(round_pairings)
        # Xoay vòng (giữ player đầu tiên cố định)
        players = [players[0]] + [players[-1]] + players[1:-1]

    return rounds


def generate_knockout_pairings(player_ids: list[uuid.UUID]) -> list[tuple[uuid.UUID, uuid.UUID]]:
    """
    Tạo cặp đấu cho vòng knockout (1 vòng).
    Shuffle ngẫu nhiên rồi ghép cặp.
    """
    players = list(player_ids)
    random.shuffle(players)
    pairings: list[tuple[uuid.UUID, uuid.UUID]] = []
    for i in range(0, len(players) - 1, 2):
        pairings.append((players[i], players[i + 1]))
    return pairings


def generate_swiss_pairings(
    participants: list[uuid.UUID],
    previous_matches: list[Match],
) -> list[tuple[uuid.UUID, uuid.UUID]]:
    """
    Tạo cặp đấu Swiss sử dụng py4swiss (FIDE Dutch system).
    Fallback sang thuật toán đơn giản nếu py4swiss không khả dụng.
    """
    try:
        return _swiss_with_py4swiss(participants, previous_matches)
    except Exception:
        # Fallback nếu py4swiss fail
        return _swiss_fallback(participants, previous_matches)


def _swiss_with_py4swiss(
    participants: list[uuid.UUID],
    previous_matches: list[Match],
) -> list[tuple[uuid.UUID, uuid.UUID]]:
    """Swiss pairing sử dụng py4swiss library (FIDE Dutch system)."""
    from py4swiss import Swiss

    # Map UUID → int index cho py4swiss
    id_to_idx = {pid: i + 1 for i, pid in enumerate(participants)}
    idx_to_id = {i + 1: pid for i, pid in enumerate(participants)}

    # Tạo tournament object
    tournament = Swiss(len(participants))

    # Thêm kết quả các vòng trước
    for match in previous_matches:
        if match.result == MatchResult.pending:
            continue
        w_idx = id_to_idx.get(match.white_player_id)
        b_idx = id_to_idx.get(match.black_player_id)
        if w_idx is None or b_idx is None:
            continue

        if match.result == MatchResult.white_win:
            tournament.add_result(w_idx, b_idx, "1-0")
        elif match.result == MatchResult.black_win:
            tournament.add_result(w_idx, b_idx, "0-1")
        elif match.result == MatchResult.draw:
            tournament.add_result(w_idx, b_idx, "1/2-1/2")

    # Generate pairings cho vòng tiếp theo
    raw_pairings = tournament.make_round()

    pairings: list[tuple[uuid.UUID, uuid.UUID]] = []
    for white_idx, black_idx in raw_pairings:
        white_id = idx_to_id.get(white_idx)
        black_id = idx_to_id.get(black_idx)
        if white_id and black_id:
            pairings.append((white_id, black_id))

    return pairings


def _swiss_fallback(
    participants: list[uuid.UUID],
    previous_matches: list[Match],
) -> list[tuple[uuid.UUID, uuid.UUID]]:
    """
    Fallback Swiss pairing khi py4swiss không khả dụng.
    Quy tắc:
    1. Ghép theo điểm gần nhau nhất (score groups)
    2. Tránh ghép lại cặp đã đấu
    3. Cân bằng màu quân (ai cầm trắng nhiều hơn sẽ cầm đen)
    """
    scores: dict[uuid.UUID, float] = {pid: 0.0 for pid in participants}
    played_pairs: set[frozenset[uuid.UUID]] = set()
    white_count: dict[uuid.UUID, int] = {pid: 0 for pid in participants}
    black_count: dict[uuid.UUID, int] = {pid: 0 for pid in participants}

    for match in previous_matches:
        pair = frozenset([match.white_player_id, match.black_player_id])
        played_pairs.add(pair)

        # Tính điểm
        if match.result == MatchResult.white_win:
            scores[match.white_player_id] = scores.get(match.white_player_id, 0) + 1.0
        elif match.result == MatchResult.black_win:
            scores[match.black_player_id] = scores.get(match.black_player_id, 0) + 1.0
        elif match.result == MatchResult.draw:
            scores[match.white_player_id] = scores.get(match.white_player_id, 0) + 0.5
            scores[match.black_player_id] = scores.get(match.black_player_id, 0) + 0.5

        # Đếm số lần cầm trắng/đen
        if match.white_player_id in white_count:
            white_count[match.white_player_id] += 1
        if match.black_player_id in black_count:
            black_count[match.black_player_id] += 1

    # Sắp xếp theo điểm giảm dần, random tiebreak
    sorted_players = sorted(participants, key=lambda p: (-scores.get(p, 0), random.random()))

    pairings: list[tuple[uuid.UUID, uuid.UUID]] = []
    paired: set[uuid.UUID] = set()

    for i, player in enumerate(sorted_players):
        if player in paired:
            continue
        for j in range(i + 1, len(sorted_players)):
            opponent = sorted_players[j]
            if opponent in paired:
                continue
            pair = frozenset([player, opponent])
            if pair in played_pairs:
                continue

            # Xác định màu quân dựa trên color balance
            white, black = _assign_colors(player, opponent, white_count, black_count)
            pairings.append((white, black))
            paired.add(player)
            paired.add(opponent)
            break

    return pairings


def _assign_colors(
    p1: uuid.UUID, p2: uuid.UUID,
    white_count: dict[uuid.UUID, int], black_count: dict[uuid.UUID, int],
) -> tuple[uuid.UUID, uuid.UUID]:
    """
    Gán màu quân cân bằng.
    Ưu tiên: ai cầm trắng ít hơn sẽ cầm trắng.
    """
    p1_balance = white_count.get(p1, 0) - black_count.get(p1, 0)
    p2_balance = white_count.get(p2, 0) - black_count.get(p2, 0)

    if p1_balance < p2_balance:
        return (p1, p2)  # p1 cầm trắng (đã cầm ít hơn)
    elif p2_balance < p1_balance:
        return (p2, p1)  # p2 cầm trắng
    else:
        # Bằng nhau → random
        if random.random() < 0.5:
            return (p1, p2)
        return (p2, p1)
