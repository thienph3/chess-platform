# VCC Platform — Vinamilk Chess Club

Hệ thống quản lý CLB Cờ Vinamilk. Hỗ trợ 3 bộ môn: Cờ vua, Cờ tướng, Cờ vây.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────────┐
│  Frontend   │────▶│   Backend    │────▶│  Analysis Services  │
│  React+MUI  │     │   FastAPI    │     │  Stockfish/Pikafish │
│  port 5173  │     │   port 8000  │     │  KataGo (8001-8003) │
└─────────────┘     └──────┬───────┘     └─────────────────────┘
                           │
                    ┌──────▼───────┐
                    │  PostgreSQL  │
                    │   port 5432  │
                    └──────────────┘
```

## Tech Stack

| Layer | Công nghệ |
|-------|-----------|
| Frontend | React 18, TypeScript, MUI v6, TanStack Query, Vite |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Alembic |
| Database | PostgreSQL 16 |
| Analysis | Stockfish 17, Pikafish, KataGo |
| Infra | Docker Compose |

## Quick Start

```bash
# 1. Clone & setup
git clone <repo-url> && cd vcc-platform

# 2. Start all services
docker compose up -d

# 3. Run migrations
cd backend && alembic upgrade head

# 4. Frontend dev (nếu không dùng Docker)
cd frontend && npm install && npm run dev

# 5. Backend dev (nếu không dùng Docker)
cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload
```

Truy cập:
- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/api/docs
- Health check: http://localhost:8000/health

## Project Structure

```
vcc-platform/
├── backend/           # FastAPI (modular monolith)
│   ├── app/
│   │   ├── core/      # Config, exceptions, rate limiting
│   │   ├── modules/   # Feature modules (auth, members, tournaments, ...)
│   │   ├── shared/    # Base models, shared schemas
│   │   └── db/        # Database session
│   ├── alembic/       # Migrations
│   └── pyproject.toml
├── frontend/          # React SPA
│   ├── src/
│   │   ├── features/  # Feature modules (mirrors backend)
│   │   ├── components/# Shared components
│   │   ├── api/       # Axios client
│   │   └── theme/     # MUI theme
│   └── package.json
├── analysis/          # Engine services (separate containers)
│   ├── chess/         # Stockfish (port 8001)
│   ├── xiangqi/       # Pikafish (port 8002)
│   └── go/            # KataGo (port 8003)
├── docs/              # Feature documentation
├── .kiro/steering/    # AI coding conventions
└── docker-compose.yml
```

## Features

Xem chi tiết: [docs/FEATURES.md](docs/FEATURES.md)

- Quản lý thành viên, giải đấu, ELO rating, tài chính
- Chơi cờ online real-time (WebSocket) với server-side validation
- Phân tích ván đấu bằng engine (Stockfish/Pikafish/KataGo)
- Dashboard, achievements, attendance, news, gallery

## Environment Variables

Copy `.env.example` → `.env` trong mỗi folder:

```bash
cp backend/.env.example backend/.env
```

Xem `backend/.env.example` để biết các biến cần thiết.

## Development

- Backend: `cd backend && uvicorn app.main:app --reload`
- Frontend: `cd frontend && npm run dev`
- Lint: `cd backend && ruff check .`
- Format: `cd backend && ruff format .`
