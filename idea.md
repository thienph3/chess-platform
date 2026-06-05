# VCC Platform — Vinamilk Chess Club

## Tổng quan

Hệ thống quản lý toàn diện cho CLB Cờ Vinamilk, hỗ trợ 3 bộ môn: Cờ vua, Cờ tướng, Cờ vây.
Bao gồm quản lý thành viên, giải đấu, xếp hạng ELO, tài chính, chơi cờ trực tuyến, và phân tích AI.

## Tech Stack

| Layer | Công nghệ |
|-------|-----------|
| Backend | Python 3.11 + FastAPI (async) |
| ORM | SQLAlchemy 2.0 (async) + Alembic |
| Database | PostgreSQL 16 |
| Frontend | React 19 + TypeScript + MUI v7 |
| State | TanStack Query v5 |
| Build | Vite 6 |
| Real-time | WebSocket (FastAPI) |
| Analysis | Stockfish 17, Pikafish, KataGo |
| Auth | JWT (access + refresh tokens) |
| i18n | i18next |
| Charts | Recharts |
| Deploy | Docker Compose |

## Modules

### Core (✅ Hoàn thành)
1. **Auth** — Đăng nhập/đăng ký, JWT, roles (admin/member)
2. **Members** — CRUD thành viên, search, detail + stats
3. **Tournaments** — Tạo giải, đăng ký, pairing (round robin/swiss/knockout), standings
4. **Ratings** — ELO 12 slots (3 game types × 4 time formats), leaderboard, history chart
5. **Finance** — Thu chi, balance, báo cáo theo tháng/quý

### Extended (✅ Hoàn thành)
6. **Online Play** — Chơi cờ real-time (WebSocket), lobby, spectator, game history/replay
7. **Analysis** — AI phân tích (Stockfish/Pikafish/KataGo), eval bar, game review
8. **Dashboard** — Tổng quan CLB, stats cards

### Additional (✅ Hoàn thành)
9. **Achievements** — Huy hiệu, thành tích
10. **Attendance** — Điểm danh sinh hoạt
11. **News** — Tin tức CLB
12. **Notifications** — Thông báo (bell, mark read)
13. **Seasons** — Mùa giải
14. **Admin** — Quản trị hệ thống (user management, roles)
15. **Training** — Luyện tập
16. **Gallery** — Thư viện ảnh

## Kiến trúc

```
vcc-platform/
├── backend/          # FastAPI modular monolith
│   ├── app/
│   │   ├── core/     # Config, auth, exceptions
│   │   ├── modules/  # 11 feature modules
│   │   ├── shared/   # Base model, schemas
│   │   └── db/       # Session, migrations
│   └── alembic/      # DB migrations
├── frontend/         # React SPA
│   └── src/
│       ├── features/ # 14 feature modules
│       ├── api/      # Axios client
│       ├── components/ # Shared components
│       └── theme/    # MUI theme
├── analysis/         # AI analysis microservices
│   ├── chess/        # Stockfish (port 8001)
│   ├── xiangqi/     # Pikafish (port 8002)
│   └── go/          # KataGo (port 8003)
└── docker-compose.yml
```

## Còn thiếu / Cần cải thiện

### High Priority
- [ ] Server-side validation cho Xiangqi moves (Pikafish)
- [ ] Server-side validation cho Go moves (KataGo)
- [ ] Error boundaries cho mỗi route

### Medium Priority
- [ ] Spectator delay cho giải chính thức (anti-cheat)
- [ ] Mobile responsive board
- [ ] Rate limiting cho login endpoint

### Low Priority
- [ ] Puzzle generation từ ván đấu thực
- [ ] AI coaching / training mode nâng cao
- [ ] Gallery upload ảnh sự kiện
- [ ] News rich text editor
