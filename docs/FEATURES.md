# VCC Platform — Danh sách tính năng

## Tổng quan

Nền tảng quản lý và thi đấu cờ cho CLB Cờ Vinamilk (VCC).  
Hỗ trợ **4 bộ môn**: Cờ vua, Cờ tướng, Cờ vây, Cờ caro (Gomoku).

---

## Tính năng đã hoàn thành

### 1. Xác thực & Phân quyền (Auth) ✅
- Đăng nhập / Đăng ký tài khoản
- Quên mật khẩu / Đặt lại mật khẩu qua email
- JWT token (access + refresh)
- Phân quyền: Admin / Thành viên

### 2. Quản lý thành viên ✅
- Danh sách, tìm kiếm, lọc thành viên
- Trang chi tiết: thông tin cá nhân, thống kê, lịch sử thi đấu
- Upload avatar
- Bảng rating theo bộ môn

### 3. Giải đấu ✅
- **Chế độ**: Online (thi đấu trực tuyến) / OTB (thi đấu trực tiếp)
- **Thể thức**: Swiss (FIDE Dutch), Round Robin, Knockout
- Ghép cặp tự động (py4swiss) với cân bằng màu quân
- Bảng xếp hạng giải, bracket knockout
- Lịch đấu dạng calendar
- Phòng đấu tự động tạo từ cặp đấu (online mode)
- Nhập kết quả + PGN cho OTB
- Scheduled start + countdown cho ván đấu giải

### 4. Hệ thống ELO ✅
- 16 bảng xếp hạng: 4 bộ môn × 4 thể thức (bullet/blitz/rapid/standard)
- Công thức FIDE: K=40 (mới), K=20 (< 2400), K=10 (≥ 2400)
- Rating khởi điểm: 1500, sàn: 100
- Lịch sử thay đổi rating theo biểu đồ
- Tùy chọn ván đấu rated / unrated

### 5. Tài chính ✅
- Thu/chi CRUD cho CLB
- Số dư tổng + theo giải đấu
- Báo cáo theo tháng/quý
- Biểu đồ tài chính (Recharts)

### 6. Chơi cờ trực tuyến ✅
- WebSocket real-time cho 4 loại bàn cờ:
  - **Cờ vua**: react-chessboard (kéo thả)
  - **Cờ tướng**: react-xiangqiboard (kéo thả)
  - **Cờ vây**: SVG board 9/13/19 (click đặt quân)
  - **Cờ caro**: SVG board 15×15 (click đặt quân, highlight nước cuối, đường thắng)
- Đồng hồ countdown + Fischer increment
- Thanh đánh giá (EvalBar) cho cờ vua
- Xem trực tiếp (Spectator mode)
- Xem lại ván đấu (Replay)
- Xuất PGN
- Chat trong ván đấu
- Đầu hàng / Cầu hòa / Chấp nhận hòa

### 7. Dịch vụ phân tích (Analysis Services) ✅
- 4 engine chạy riêng biệt trong container:
  - **Stockfish 17** (Cờ vua) — port 8001
  - **Pikafish** (Cờ tướng) — port 8002
  - **KataGo** (Cờ vây) — port 8003
  - **Rapfi** (Cờ caro/Gomoku) — port 8004
- Validate nước đi real-time
- Phân tích thế cờ (evaluation, best move, variations)
- Gợi ý nước đi (hint)
- Review ván đấu (accuracy, phân loại nước đi)

### 8. Chơi với máy (Play vs AI) ✅
- Chọn bộ môn: Cờ vua / Cờ tướng / Cờ vây / Cờ caro
- Chọn độ khó: Dễ / Trung bình / Khó
- Chọn màu quân: Trắng / Đen / Ngẫu nhiên
- Chọn thể thức thời gian (1+0 đến 15+0, tùy chỉnh)
- AI phản hồi nước đi trong 3 giây
- Lưu lịch sử ván đấu

### 9. Tìm đối thủ (Matchmaking) ✅
- Tự động ghép cặp theo rating
- Thách đấu trực tiếp (challenge) — chọn bộ môn + thể thức

### 10. Dashboard ✅
- Thống kê tổng quan: số ván, tỷ lệ thắng, rating hiện tại
- Activity feed (hoạt động gần đây)

### 11. Huy hiệu thành tích ✅
- Hệ thống achievement cho thành viên
- Tự động trao khi đạt điều kiện

### 12. Điểm danh ✅
- Check-in tham gia hoạt động CLB
- Thống kê tần suất tham gia

### 13. Tin tức CLB ✅
- CRUD bài viết
- Rich text editor
- Ghim bài quan trọng

### 14. Thông báo ✅
- Thông báo in-app (bell icon)
- Đánh dấu đã đọc

### 15. Mùa giải ✅
- Quản lý mùa giải (seasons)
- Gắn giải đấu vào mùa

### 16. Quản trị (Admin) ✅
- Quản lý tài khoản
- Phân quyền role-based

### 17. Luyện tập ✅
- Trang training cơ bản

### 18. Thư viện ảnh ✅
- Upload ảnh sự kiện
- Xem / Xóa gallery

### 19. Xử lý lỗi ✅
- ErrorBoundary per route
- Nút retry khi lỗi
- Loading state (spinner) cho lazy-loaded pages

### 20. Khai cuộc (Opening Explorer) ✅
- Tra cứu khai cuộc cờ vua

---

## Tính năng chưa triển khai

| # | Tính năng | Mô tả | Priority |
|---|-----------|--------|----------|
| 21 | Puzzle generation | Tự động tạo bài tập từ ván đấu thực (phát hiện sai lầm) | 🟢 |
| 22 | AI coaching | Chế độ luyện tập nâng cao với gợi ý từ engine | 🟢 |
| 23 | Mobile responsive boards | Bàn cờ scale theo viewport + hỗ trợ touch | 🟢 |

---

## Deployment

- **Dev**: `dev-ml.tech.vinamilklocal.com/chess`
- **Infra**: EKS (Kubernetes) + ECR + Helm + Skaffold
- **Database**: PostgreSQL trên RDS
- **CI/CD**: `aws-vault exec data-dev -- skaffold run -p dev`
