# Ratings — Hệ thống ELO ✅

## Trạng thái: Hoàn thành

## Đã implement

### Backend
- `GET /api/v1/leaderboard` — Bảng xếp hạng (query: game_type, time_format, limit)
- `GET /api/v1/ratings/:member_id` — Ratings hiện tại của thành viên
- `GET /api/v1/ratings/:member_id/history` — Lịch sử thay đổi rating
- `POST /api/v1/ratings/calculate` — Tính ELO cho 1 ván đấu (option `rated: true/false`)

### ELO Algorithm (FIDE standard, áp dụng cho cả 4 môn)
- Rating khởi điểm: 1500 (FIDE standard cho unrated players)
- Rating floor: 100 (không thể xuống dưới)
- K-factor (theo FIDE):
  - K=40: player mới (< 30 rated games)
  - K=20: player có rating < 2400
  - K=10: player có rating >= 2400
- Formula: `new = old + K * (actual - expected)`
- Expected: `1 / (1 + 10^((opp - player) / 400))`
- 16 rating slots: 4 game types × 4 time formats
- Option `rated`: ván đấu có thể chọn không tính ELO (friendly/import lịch sử)

### Frontend
- Leaderboard page: tabs game type + dropdown time format + DataGrid
- Rating chart (trong member detail): Recharts line chart, filter theo game_type + time_format
- Hook `useRatingHistory` + `useMemberRatings`

### Database
- Table `ratings`: member_id, game_type, time_format, rating, games_played, wins, draws, losses
- Table `rating_changes`: rating_id, match_id, old_rating, new_rating, change
- Unique constraint: (member_id, game_type, time_format)
