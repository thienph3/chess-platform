# Dashboard — Trang chủ ✅

## Trạng thái: Hoàn thành

## Đã implement

### Frontend
- Tổng số thành viên (từ API members)
- Số giải đấu đang diễn ra (filter status=in_progress)
- Số dư CLB hiện tại (từ API finance/balance)
- Cards điều hướng nhanh đến từng module
- Skeleton loading state
- Hook `useDashboardStats` gọi 3 API song song

### Trang UI
- Route: `/` (index)
- Grid 4 cards: Thành viên, Giải đấu đang diễn ra, Bảng xếp hạng, Số dư CLB
- Click card → navigate đến module tương ứng
