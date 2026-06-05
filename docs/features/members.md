# Members — Quản lý thành viên ✅

## Trạng thái: Hoàn thành

## Đã implement

### Backend
- `GET /api/v1/members` — Danh sách (paginated, search by name)
- `GET /api/v1/members/:id` — Chi tiết
- `POST /api/v1/members` — Tạo mới
- `PATCH /api/v1/members/:id` — Cập nhật
- `DELETE /api/v1/members/:id` — Xóa mềm (soft delete)
- Search: `?search=...` filter theo full_name (ilike)
- Repository pattern + Service layer + DI

### Frontend
- Danh sách: DataGrid + server-side pagination
- Search bar: tìm kiếm theo tên (debounced)
- Form dialog: thêm/sửa thành viên (React Hook Form + Zod)
- Snackbar feedback (success/error)
- Click row → navigate đến detail page
- Detail page `/members/:id`:
  - Header: tên, email, phone, skill level chip
  - Tab Hồ sơ: ngày tham gia, ghi chú
  - Tab Lịch sử giải đấu: placeholder
  - Tab ELO Ratings: biểu đồ rating (Recharts line chart) với filter game_type + time_format

### Database
- Table `members`: id, full_name, email, phone, skill_level, notes, is_deleted, created_at, updated_at

## Fields
- full_name (required)
- email (unique, optional)
- phone (optional)
- skill_level: beginner / intermediate / advanced
- notes (optional)
