# Online Play — Chơi cờ trực tiếp ✅

## Architecture

```
Client (WebSocket) → Backend (stateless relay, giữ FEN state)
                        ↓ HTTP
                   Analysis Service (validate + analyze + PGN)
```

Backend KHÔNG chứa game logic. Mọi validation được delegate sang Analysis Services.

## Game Modes

- **Casual**: tạo phòng tự do, ai cũng join được
- **AI**: chơi với máy (difficulty easy/medium/hard, chọn màu/thể thức)
- **Tournament**: room tạo từ match, scheduled_start, board locked đến giờ

## Scheduled Start (Tournament games)

- `game_rooms.scheduled_start` — thời điểm bắt đầu
- Player vào room sớm: thấy board + countdown, không đi được
- Đúng giờ: frontend unlock board, clock bắt đầu chạy
- Nếu player không vào: hết giờ → forfeit

## API

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | /api/v1/games | Tạo phòng chơi (requires auth) |
| GET | /api/v1/games/live | Danh sách phòng đang chờ/đang chơi |
| GET | /api/v1/games/:id | Thông tin phòng |
| POST | /api/v1/games/:id/join | Tham gia phòng |
| GET | /api/v1/games/:id/moves | Lịch sử nước đi |
| GET | /api/v1/games/:id/pgn | Export PGN (gọi analysis service) |
| POST | /api/v1/games/from-match/:match_id | Tạo phòng từ ván đấu giải |
| WS | /ws/game/:id | WebSocket real-time gameplay |

## WebSocket Protocol

```
Client → Server:
  { "type": "init", "game_type": "chess" }
  { "type": "move", "from": "e2", "to": "e4", "promotion": "q" }  // Chess
  { "type": "move", "from_row": 9, "from_col": 4, "to_row": 8, "to_col": 4 }  // Xiangqi
  { "type": "move", "row": 3, "col": 3 }  // Go
  { "type": "move", "row": 7, "col": 7 }  // Gomoku (15×15 board)
  { "type": "pass" }  // Go only
  { "type": "resign" }
  { "type": "draw_offer" }
  { "type": "draw_accept" }
  { "type": "chat", "message": "..." }

Server → Client:
  { "type": "state", "game_type": "chess", "fen": "...", "turn": "white", "game_over": false }
  { "type": "move", ..., "fen": "...", "turn": "..." }
  { "type": "game_over", "result": "white_win", "reason": "checkmate" }
  { "type": "error", "message": "Nước đi không hợp lệ" }
  { "type": "resign", "by": "opponent" }
  { "type": "draw_offered" }
  { "type": "chat", "message": "...", "sender": "player" }
```

## Move Validation Flow

1. Client gửi move qua WebSocket
2. Backend gọi `POST analysis-service/api/v1/validate` với FEN + move
3. Analysis service validate bằng engine binary, trả về valid/invalid + new FEN
4. Nếu valid: cập nhật state, broadcast cho tất cả clients
5. Nếu invalid: gửi error cho client gửi move

## Board Components (Frontend)

| Bộ môn | Component | Interaction |
|--------|-----------|-------------|
| Chess | react-chessboard | Drag & drop |
| Xiangqi | react-xiangqiboard | Drag & drop |
| Go | Custom SVG | Click to place |
| Gomoku | Custom SVG (15×15 grid) | Click to place |

## Features

- Đồng hồ countdown (GameClock component, highlight đỏ < 30s)
- EvalBar (thanh đánh giá, Chess)
- Spectator mode (read-only board, real-time)
- Spectator delay (configurable per tournament, anti-cheat)
- Game replay (step through moves)
- PGN export (gọi analysis service)
- Chat in-game
- Resign + draw offer/accept
- Tournament integration (auto-create room from match)

## Database

- `game_rooms`: match_id, white/black_player_id, status, game_type, time_control, fen, result, accuracy scores
- `move_history`: room_id, move_number, notation, fen_after
