# Finance — Quản lý tài chính ✅

## Trạng thái: Hoàn thành

## Đã implement

### Backend
- `GET /api/v1/transactions` — Danh sách (paginated, filter: type, category, date_from, date_to, tournament_id)
- `POST /api/v1/transactions` — Tạo giao dịch
- `PATCH /api/v1/transactions/:id` — Cập nhật
- `DELETE /api/v1/transactions/:id` — Xóa mềm
- `GET /api/v1/finance/balance` — Balance tổng CLB
- `GET /api/v1/finance/balance/:tournament_id` — Balance theo giải
- `GET /api/v1/finance/report` — Báo cáo (query: year, period=monthly|quarterly)

### Categories
- Thu: membership_fee, sponsorship, donation, other_income
- Chi: venue, prize, equipment, food, other_expense

### Frontend
- Tabs: Giao dịch + Báo cáo
- Tab Giao dịch: DataGrid + filter loại (thu/chi) + click row để sửa
- Tab Báo cáo: Recharts bar chart thu vs chi theo tháng/quý, filter năm + kỳ
- Balance cards: tổng thu, tổng chi, số dư
- Form dialog: thêm/sửa giao dịch (type → category dynamic)

### Database
- Table `transactions`: type, category, amount, date, description, member_id, tournament_id
