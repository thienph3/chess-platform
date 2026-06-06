# Online Play — Chơi cờ trực tiếp ✅

## Kiến trúc

```
Client (WebSocket) → Backend (auth + turn enforcement + server clock)
                        ↓ HTTP
                   Analysis Service (validate + suggest)
                        ↓
                      Redis (game state + clock + pub/sub)
```

## Game Flow (Human vs Human)

```
Create room → Join → Both Ready → 5s Countdown → Playing → Finished
```

1. Player 1 tạo phòng (game_type, time_control, increment)
2. Player 2 tham gia
3. Cả 2 nhấn "Sẵn sàng" → server đếm ngược 5s
4. Game start → clock bắt đầu chạy
5. Kết thúc: thắng / hết giờ / đầu hàng / hòa

## Game Flow (Human vs AI)

Giống hệt Human vs Human — AI là bot player:

1. Player tạo phòng AI (chọn bộ môn, độ khó, thể thức)
2. Bot tự động join + ready
3. Countdown → start
4. Bot tự đi nước khi đến lượt (gọi analysis service)
5. Cùng clock, cùng protocol, cùng GamePlayPage

## Server Clock (Source of Truth)

- Clock lưu trong Redis, deduct khi player đi nước
- Fischer increment: cộng sau mỗi nước đi
- Timeout: server check mỗi 1s, hết giờ = thua
- Disconnect: clock vẫn chạy, player có thể reconnect

## WebSocket Protocol

```
WS URL: /ws/game/{room_id}?token=JWT

Client → Server:
  { "type": "ready" }
  { "type": "unready" }
  { "type": "move", "from": "e2", "to": "e4" }         // Chess/Xiangqi
  { "type": "move", "row": 7, "col": 7 }               // Gomoku/Go
  { "type": "resign" }
  { "type": "draw_offer" }
  { "type": "draw_accept" }
  { "type": "chat", "message": "..." }

Server → Client:
  { "type": "waiting", "role": "white", "players_connected": 1, ... }
  { "type": "ready_status", "ready_count": 1, "needed": 2 }
  { "type": "countdown", "seconds": 5 }
  { "type": "game_start", "fen", "turn", "white_clock", "black_clock" }
  { "type": "move", ..., "fen", "turn", "white_clock", "black_clock" }
  { "type": "game_over", "result", "reason", "white_clock", "black_clock" }
  { "type": "error", "message" }
  { "type": "player_disconnected", "role", "players_connected" }
  { "type": "draw_offered" }
  { "type": "chat", "message", "sender" }
```

## Bảo mật

- **Auth**: JWT token qua query param → xác định player role (white/black/spectator)
- **Turn enforcement**: chỉ player đúng lượt mới đi được
- **Spectator isolation**: xem được, không tương tác được
- **Draw offer**: chỉ gửi cho đối thủ, không broadcast

## Multi-pod Support

- Redis pub/sub: broadcast nước đi giữa các pod
- Game state trong Redis: player reconnect vào pod khác vẫn OK
- Clock trong Redis: không mất khi pod restart

## Board Components (Frontend)

| Bộ môn | Component | Style |
|--------|-----------|-------|
| Chess | react-chessboard | Kéo thả |
| Xiangqi | react-xiangqiboard | Kéo thả |
| Go | GoBoard (SVG) | Click đặt quân tròn |
| Gomoku | GomokuBoard (SVG) | Click đặt X/O trên giao điểm |

## Room Timeout

| Trạng thái | Timeout | Hành động |
|---|---|---|
| Waiting (không ai join) | 30 phút | Aborted |
| Playing (bỏ ván) | 2 giờ | Draw |
| All disconnect khi playing | 30s grace → clock timeout | Thua |

## API

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | /games | Tạo phòng |
| GET | /games/live | Danh sách phòng |
| GET | /games/:id | Chi tiết phòng |
| POST | /games/:id/join | Tham gia |
| POST | /games/:id/cancel | Hủy phòng |
| GET | /games/:id/moves | Lịch sử nước đi |
| POST | /games/ai/start | Tạo ván AI (bot auto-join) |
| WS | /ws/game/:id?token=JWT | Real-time gameplay |
