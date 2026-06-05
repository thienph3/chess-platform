# Tournaments — Quản lý giải đấu ✅

## Tournament Modes

### Online
- Admin tạo giải (mode=online) → tạo round với `start_time`
- Admin click "Tạo phòng" → hệ thống tạo game rooms cho mỗi match (scheduled_start = start_time)
- Kì thủ vào room sớm (xem board, chat), board locked
- Đúng giờ → countdown hết → board unlock, đồng hồ chạy
- Kết quả tự động cập nhật match khi game over

### OTB (Over The Board)
- Admin tạo giải (mode=otb) → tạo round (không cần start_time)
- Kì thủ chơi ngoài đời
- Admin nhập kết quả: chọn 1-0 / 0-1 / ½-½ + PGN (optional)

## API

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| GET | /tournaments | Danh sách (paginated, filter status + game_type) |
| GET | /tournaments/:id | Chi tiết |
| POST | /tournaments | Tạo giải (name, game_type, time_format, format, mode, max_participants) |
| PATCH | /tournaments/:id | Cập nhật |
| DELETE | /tournaments/:id | Xóa mềm |
| POST | /tournaments/:id/participants | Đăng ký tham gia |
| GET | /tournaments/:id/participants | Danh sách participants |
| POST | /tournaments/:id/generate-pairings | Tạo cặp đấu tự động |
| POST | /tournaments/:id/rounds | Tạo vòng (round_number, start_time) |
| GET | /tournaments/:id/rounds | Danh sách vòng + matches |
| POST | /tournaments/:id/rounds/:round_id/create-rooms | Tạo game rooms cho round (online) |
| GET | /tournaments/:id/standings | Bảng xếp hạng giải |
| PATCH | /matches/:id/result | Nhập kết quả (result, pgn) |

## Pairing Algorithms

- **Round Robin**: full schedule (n-1 vòng), xen kẽ trắng/đen
- **Swiss**: py4swiss (FIDE Dutch system) + fallback với color balance, avoid repeat
- **Knockout**: random bracket, loại trực tiếp

## Standings & Tiebreak

- Điểm: thắng=1, hòa=0.5, thua=0
- Buchholz → Sonneborn-Berger → số thắng

## Frontend

- Danh sách: DataGrid + filter + nút tạo giải + lịch
- Calendar view: grid theo tháng
- Detail page (3 tabs): Thông tin, Người tham gia, Lịch đấu
- Lịch đấu:
  - Online: "Tạo phòng" (admin) + "Chơi" (player) buttons
  - OTB: "Nhập KQ" (admin) → dialog chọn result + PGN
  - Knockout: bracket visualization

## Database

- Tables: tournaments, tournament_participants, tournament_rounds, matches
- Fields mới: `tournaments.mode` (online/otb), `tournament_rounds.start_time`, `game_rooms.scheduled_start`
