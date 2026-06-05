"""
ELO calculation theo chuẩn FIDE, áp dụng cho cả 3 môn (Chess, Xiangqi, Go).

FIDE K-factor rules (adapted cho CLB):
- K=40: player mới (< 30 rated games)
- K=20: player có rating < 2400
- K=10: player có rating >= 2400

Công thức:
- Expected score: E = 1 / (1 + 10^((R_opponent - R_player) / 400))
- New rating: R_new = R_old + K * (S_actual - S_expected)
- S_actual: 1.0 (thắng), 0.5 (hòa), 0.0 (thua)

Rating khởi điểm: 1500 (FIDE standard cho unrated players)
Rating floor: 100 (không thể xuống dưới)
"""

INITIAL_RATING = 1500
RATING_FLOOR = 100


def get_k_factor(rating: int, games_played: int) -> int:
    """
    K-factor theo FIDE rules (adapted).

    - K=40: Dưới 30 ván rated (new player, rating biến động nhanh)
    - K=20: Rating < 2400 (standard player)
    - K=10: Rating >= 2400 (experienced/strong player, rating ổn định)
    """
    if games_played < 30:
        return 40
    if rating < 2400:
        return 20
    return 10


def expected_score(player_rating: int, opponent_rating: int) -> float:
    """
    Expected score (xác suất thắng) theo FIDE formula.

    Ý nghĩa:
    - Chênh 0 điểm → E = 0.5 (50%)
    - Chênh 200 điểm → E ≈ 0.76 (76% cho người mạnh hơn)
    - Chênh 400 điểm → E ≈ 0.91 (91%)
    """
    return 1.0 / (1.0 + 10 ** ((opponent_rating - player_rating) / 400))


def calculate_new_rating(
    player_rating: int,
    opponent_rating: int,
    actual_score: float,
    games_played: int,
) -> int:
    """
    Tính rating mới theo FIDE ELO formula.

    Args:
        player_rating: Rating hiện tại.
        opponent_rating: Rating đối thủ.
        actual_score: 1.0 (thắng), 0.5 (hòa), 0.0 (thua).
        games_played: Số ván rated đã chơi (để xác định K-factor).

    Returns:
        Rating mới (không thấp hơn RATING_FLOOR).
    """
    k = get_k_factor(player_rating, games_played)
    expected = expected_score(player_rating, opponent_rating)
    new_rating = player_rating + k * (actual_score - expected)
    return max(RATING_FLOOR, round(new_rating))
