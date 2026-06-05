# UX Enhancements ✅

## Trạng thái: Phần lớn hoàn thành

## Đã implement

### Detail Pages
- `/members/:id` — Header + 3 tabs (Hồ sơ, Giải đấu, ELO chart)
- `/tournaments/:id` — Header + 3 tabs (Thông tin, Participants, Lịch đấu)
- Back button navigation
- Skeleton loading
- Not found state

### Biểu đồ
- ELO rating line chart (Recharts) — trong member detail, filter game_type + time_format
- Finance bar chart (Recharts) — thu vs chi theo tháng/quý, filter năm + kỳ

### Search & Filter
- Members: search bar (tìm theo tên, server-side ilike)
- Tournaments: filter trạng thái + bộ môn
- Finance: filter loại (thu/chi)

### Empty States
- Shared `EmptyState` component (icon + message + CTA button)
- Sử dụng trong Game Lobby khi chưa có phòng

### Loading States
- Skeleton cho mọi trang (MUI Skeleton)
- Button disabled khi submitting form
- isPending state cho mutations

### Notifications
- Snackbar (MUI) cho success/error sau mỗi action
- Alert inline cho form errors

### Layout
- Sidebar navigation cố định (6 items + logout)
- Hiển thị email user đang login
- Responsive (MUI breakpoints)

## Chưa implement
- Breadcrumb navigation (component đã có nhưng chưa dùng ở tất cả pages)
