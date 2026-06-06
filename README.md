# VCC Platform — Vinamilk Chess Club

Hệ thống quản lý và thi đấu cờ cho CLB Cờ Vinamilk.  
Hỗ trợ **4 bộ môn**: Cờ vua, Cờ tướng, Cờ vây, Cờ caro (Gomoku).

## Kiến trúc

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────────────┐
│  Frontend   │────▶│   Backend    │────▶│    Analysis Services     │
│  React+MUI  │     │   FastAPI    │     │  Stockfish / Pikafish    │
│             │     │   port 8000  │     │  KataGo / Rapfi          │
└─────────────┘     └──────┬───────┘     │  (8001 / 8002 / 8003    │
                           │             │   / 8004)                │
                    ┌──────▼───────┐     └──────────────────────────┘
                    │  PostgreSQL  │
                    │   (RDS)      │
                    └──────────────┘
```

## Công nghệ

| Tầng | Công nghệ |
|------|-----------|
| Frontend | React 19, TypeScript, MUI v7, TanStack Query, Vite |
| Backend | Python 3.11, FastAPI, SQLAlchemy 2.0 (async), Alembic |
| Database | PostgreSQL 16 (RDS) |
| Cờ vua | Stockfish 17 |
| Cờ tướng | Pikafish |
| Cờ vây | KataGo |
| Cờ caro | Rapfi (Gomocup protocol) |
| Infra | Docker Compose (local), EKS + Helm + Skaffold (deploy) |

## Bắt đầu nhanh (Local)

```bash
# 1. Clone
git clone <repo-url> && cd chess-platform

# 2. Khởi động tất cả services
docker compose up -d

# 3. Chạy migrations
cd backend && alembic upgrade head

# 4. Frontend dev
cd frontend && npm install && npm run dev

# 5. Backend dev
cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload
```

Truy cập:
- Frontend: http://localhost:5173
- Backend API docs: http://localhost:8000/api/docs
- Health check: http://localhost:8000/health

## Deploy lên EKS (Dev)

```bash
# Login ECR
aws-vault exec data-dev -- aws ecr get-login-password --region ap-southeast-1 | \
  docker login --username AWS --password-stdin 783163248618.dkr.ecr.ap-southeast-1.amazonaws.com

# Deploy
aws-vault exec data-dev -- skaffold run -p dev
```

URL: `http://dev-ml.tech.vinamilklocal.com/chess`

## Cấu trúc dự án

```
chess-platform/
├── backend/              # FastAPI (modular monolith)
│   ├── app/
│   │   ├── core/         # Config, exceptions, security
│   │   ├── modules/      # auth, members, tournaments, ratings,
│   │   │                 # finance, games, notifications, news,
│   │   │                 # seasons, attendance, achievements, gallery
│   │   ├── shared/       # Base models, schemas
│   │   └── db/           # Database session
│   ├── alembic/          # Migrations
│   └── tests/            # pytest + httpx (async)
├── frontend/             # React SPA
│   ├── src/
│   │   ├── features/     # Modules (mirrors backend)
│   │   ├── components/   # Shared components
│   │   ├── api/          # Axios client
│   │   ├── hooks/        # Custom hooks
│   │   ├── i18n/         # Đa ngôn ngữ (Vi/En)
│   │   └── theme/        # MUI theme (Vinamilk brand)
│   └── e2e/              # Playwright tests
├── analysis/             # Engine services (containers riêng)
│   ├── chess/            # Stockfish (port 8001)
│   ├── xiangqi/          # Pikafish (port 8002)
│   ├── go/               # KataGo (port 8003)
│   ├── gomoku/           # Rapfi (port 8004)
│   └── shared/           # Schemas + base engine chung
├── k8s/                  # Helm chart cho EKS
│   └── helm/
│       ├── templates/    # deployment, service, ingress
│       ├── values-dev.yaml
│       └── values-prod.yaml
├── docs/                 # Tài liệu tính năng
├── skaffold.yaml         # Build + deploy orchestrator
└── docker-compose.yml    # Local development
```

## Tính năng chính

- ✅ Chơi cờ online real-time (WebSocket) — 4 bộ môn
- ✅ Chơi với AI (Stockfish/Pikafish/KataGo/Rapfi)
- ✅ Giải đấu (Swiss/Round Robin/Knockout, Online/OTB)
- ✅ ELO rating (16 bảng: 4 môn × 4 thể thức)
- ✅ Quản lý thành viên, tài chính, tin tức
- ✅ Dashboard, huy hiệu, điểm danh, thư viện ảnh

Xem chi tiết: [docs/FEATURES.md](docs/FEATURES.md)

## Chạy test

```bash
# Backend unit + API tests (cần PostgreSQL)
cd backend && pytest tests/ -v

# E2E tests trên live deployment
cd backend && pytest tests/test_e2e_live.py -v

# Frontend Playwright (cần Edge/Chrome)
cd frontend && npx playwright test --config=e2e/playwright.config.ts
```

## Biến môi trường

Copy `.env.example` → `.env`:

```bash
cp backend/.env.example backend/.env
```

Xem `backend/.env.example` để biết các biến cần thiết.
