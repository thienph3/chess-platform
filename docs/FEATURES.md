# VCC Platform — Tính năng

| # | Tính năng | Mô tả | Priority | Status |
|---|-----------|--------|----------|--------|
| 1 | Auth | Login, register, forgot/reset password, JWT, roles (admin/member) | 🔴 | ✅ |
| 2 | Members | CRUD, search, detail page, stats, avatar upload | 🔴 | ✅ |
| 3 | Tournaments | Online/OTB mode, pairing (Swiss/Round Robin/Knockout), standings, bracket, calendar, scheduled rooms, OTB result input + PGN | 🔴 | ✅ |
| 4 | Ratings | ELO calculation (12 slots: 3 game types × 4 time formats), leaderboard, history chart | 🔴 | ✅ |
| 5 | Finance | Thu/chi CRUD, balance tổng + per tournament, report theo tháng/quý, biểu đồ | 🔴 | ✅ |
| 6 | Online Play | WebSocket real-time, 3 boards (Chess/Xiangqi/Go), spectator, replay, PGN export, scheduled start + countdown | 🔴 | ✅ |
| 7 | Analysis Services | 3 engines (Stockfish/Pikafish/KataGo) — validate moves, analyze, export PGN | 🔴 | ✅ |
| 8 | Play vs AI | Chơi với máy, chọn màu/difficulty/thể thức, lưu history, SAN notation | � | ✅ |
| 9 | Matchmaking | Tìm đối thủ tự động theo rating, thách đấu trực tiếp | 🟡 | ✅ |
| 10 | Dashboard | Stats tổng quan, activity feed | 🟡 | ✅ |
| 11 | Achievements | Huy hiệu thành tích cho thành viên | 🟡 | ✅ |
| 12 | Attendance | Điểm danh, thống kê tham gia | 🟡 | ✅ |
| 13 | News | Tin tức CLB, rich text editor, ghim bài | 🟡 | ✅ |
| 14 | Notifications | In-app notifications, bell icon, mark read | 🟡 | ✅ |
| 15 | Seasons | Quản lý mùa giải | 🟡 | ✅ |
| 16 | Admin | Quản lý users, phân quyền role-based | 🟡 | ✅ |
| 17 | Training | Trang luyện tập | 🟢 | ✅ |
| 18 | Gallery | Thư viện ảnh sự kiện, upload, xóa | 🟢 | ✅ |
| 19 | Error Handling | ErrorBoundary per route, retry button, rate limiting | 🟡 | ✅ |
| 20 | Swiss Pairing | py4swiss (FIDE Dutch system) + fallback với color balance | 🟡 | ✅ |
| 21 | Puzzle generation | Tự động tạo puzzle từ ván đấu thực (detect blunders) | 🟢 | 🔲 |
| 22 | AI coaching | Training mode nâng cao với engine suggestions | 🟢 | 🔲 |
| 23 | Mobile responsive boards | Chess/Xiangqi/Go board scale theo viewport + touch | 🟢 | ⏭️ |
