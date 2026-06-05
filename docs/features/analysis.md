# Analysis — Service phân tích & validation cờ

## Tổng quan

3 services riêng biệt, mỗi service chạy 1 engine binary. Chịu trách nhiệm:
- **Move validation** — validate nước đi real-time cho Online Play
- **Game analysis** — review ván đấu, tính accuracy
- **PGN export** — generate PGN chuẩn format
- **Move suggestion** — gợi ý nước đi (hint, training)

Backend KHÔNG chứa game logic — chỉ gọi analysis services qua HTTP.

## Engines

| Bộ môn | Engine | Port | Protocol |
|--------|--------|------|----------|
| Chess | Stockfish 17 | 8001 | UCI |
| Xiangqi | Pikafish | 8002 | UCI |
| Go | KataGo | 8003 | GTP |

## Tính năng

### 1. Đánh giá thế cờ (Position Evaluation)
- Input: FEN/position string + game_type
- Output: evaluation score (centipawns hoặc win%), best move, top 3 variations
- Depth configurable (quick: depth 15, deep: depth 25+)

### 2. Review ván đấu (Game Review)
- Input: danh sách nước đi (PGN/move list) + game_type
- Output: đánh giá từng nước đi:
  - Classification: brilliant / great / good / inaccuracy / mistake / blunder
  - Best move tại mỗi vị trí
  - Accuracy score tổng (0-100%)
  - Biểu đồ evaluation theo nước đi
- Async processing (ván dài có thể mất 10-30s)

### 3. Gợi ý nước đi (Move Suggestion)
- Input: FEN + game_type + difficulty level
- Output: best move + explanation (nếu có)
- Dùng cho hint trong game hoặc training mode

### 4. Puzzle Generation (tương lai)
- Tự động tạo puzzle từ ván đấu thực
- Phát hiện tactical motifs (fork, pin, skewer, etc.)

## Kiến trúc

```
analysis/
├── shared/             # Shared interface + schemas
│   ├── base_engine.py  # Abstract BaseEngine class
│   └── schemas.py      # Pydantic request/response models
├── chess/              # Port 8001 — Stockfish
│   ├── Dockerfile      # apt install stockfish
│   ├── engine.py       # python-chess UCI adapter
│   ├── main.py         # FastAPI app
│   └── pyproject.toml
├── xiangqi/            # Port 8002 — Pikafish
│   ├── Dockerfile      # Build from source (GitHub)
│   ├── engine.py       # UCI async subprocess adapter
│   ├── main.py         # FastAPI app
│   └── pyproject.toml
└── go/                 # Port 8003 — KataGo
    ├── Dockerfile      # Download binary + model b60c320
    ├── engine.py       # GTP async subprocess adapter
    ├── main.py         # FastAPI app
    └── pyproject.toml
```

Mỗi service deploy riêng, scale riêng:
- Chess: nhẹ (~50MB image), CPU thấp
- Xiangqi: nhẹ (~60MB image), CPU thấp
- Go: nặng (~350MB image do model), cần nhiều CPU hoặc GPU

## API

| Method | Endpoint | Mô tả |
|--------|----------|--------|
| POST | /api/v1/validate | Validate 1 nước đi (real-time, cho WebSocket) |
| GET | /api/v1/initial-state | Lấy FEN ban đầu + turn |
| POST | /api/v1/analyze/position | Đánh giá 1 thế cờ |
| POST | /api/v1/analyze/game | Review toàn bộ ván đấu |
| POST | /api/v1/analyze/suggest | Gợi ý nước đi tốt nhất |
| POST | /api/v1/export/pgn | Generate PGN từ move list |
| GET | /api/v1/analyze/health | Health check + engine status |

### Validate Move (dùng cho real-time gameplay)
```json
// Request
{ "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
  "move": { "from": "e7", "to": "e5" } }

// Response
{ "valid": true, "new_fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq e6 0 2",
  "turn": "white", "game_over": false, "result": null, "reason": null }
```

### Request/Response examples

#### Position Analysis
```json
// Request
{
  "game_type": "chess",
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "depth": 20,
  "num_variations": 3
}

// Response
{
  "evaluation": { "type": "cp", "value": 25 },
  "best_move": "e7e5",
  "variations": [
    { "moves": ["e7e5", "g1f3", "b8c6"], "eval": 25 },
    { "moves": ["d7d5", "e4d5", "d8d5"], "eval": 35 },
    { "moves": ["c7c5", "g1f3", "d7d6"], "eval": 40 }
  ],
  "depth_reached": 20
}
```

#### Game Review
```json
// Request
{
  "game_type": "chess",
  "moves": ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4", "g8f6"],
  "depth": 18
}

// Response
{
  "task_id": "abc-123",
  "status": "completed",
  "accuracy": { "white": 92.5, "black": 88.3 },
  "moves": [
    { "move": "e2e4", "eval_before": 0, "eval_after": 25, "best_move": "e2e4", "classification": "great" },
    { "move": "e7e5", "eval_before": 25, "eval_after": 20, "best_move": "e7e5", "classification": "great" }
  ]
}
```

## Communication với Platform

```
Frontend → Backend API (WebSocket) → Analysis Service (internal HTTP)
                                        ↓
                                   Engine process (Stockfish/Pikafish/KataGo)
```

- Backend gọi Analysis service qua Docker internal network
- Move validation: sync request (~1-5ms latency)
- Game review: heavier, có thể async với task_id + polling
- PGN export: sync request

## Deployment

- 3 Docker containers riêng biệt, deploy/scale độc lập
- Chess (port 8001): `apt install stockfish` — image ~50MB
- Xiangqi (port 8002): Pikafish build from source — image ~60MB
- Go (port 8003): KataGo eigen + model `kata1-b60c320` — image ~350MB
- Backend route request đến đúng service theo game_type
- Có thể chỉ deploy Chess + Xiangqi nếu CLB không chơi Go

## Tech Stack

| Component | Công nghệ |
|-----------|-----------|
| Framework | FastAPI (async) |
| Chess engine comm | python-chess (UCI protocol) |
| Go engine comm | Custom GTP client |
| Task queue (future) | Celery + Redis (cho heavy analysis) |
| Engine binaries | Stockfish 17, Pikafish, KataGo |

## Roadmap

| Phase | Tính năng | Trạng thái |
|-------|-----------|-----------|
| 1 | Move validation endpoint (Chess/Xiangqi/Go) | ✅ |
| 2 | Position analysis | ✅ |
| 3 | Game review + accuracy scoring | ✅ |
| 4 | Frontend integration (eval bar, move classification) | ✅ |
| 5 | Move suggestion / hint | ✅ |
| 6 | PGN export endpoint | ✅ |
| 7 | Puzzle generation | 🔲 Todo |
| 8 | AI coaching / training mode | 🔲 Todo |
