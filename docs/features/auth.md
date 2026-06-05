# Auth — Đăng nhập & Phân quyền ✅

## Trạng thái: Hoàn thành

## Đã implement

### Backend
- `POST /api/v1/auth/register` — Tạo user + member profile, hash password (bcrypt)
- `POST /api/v1/auth/login` — Verify credentials, trả JWT tokens
- `POST /api/v1/auth/refresh` — Refresh token rotation
- `GET /api/v1/auth/me` — Thông tin user hiện tại (requires auth)
- JWT: access token (30 phút) + refresh token (7 ngày)
- Roles: admin / member
- User model liên kết với Member qua `member_id`

### Frontend
- Login page: form email + password, Zod validation, redirect sau login
- Register page: form họ tên + email + password, redirect đến login
- AuthContext: quản lý user state, login/register/logout
- Token storage: localStorage (`vcc_access_token`, `vcc_refresh_token`)
- Axios interceptor: auto-attach Bearer token
- ProtectedRoute: redirect /login nếu chưa auth, skeleton khi loading
- Layout sidebar: hiển thị email + nút đăng xuất

### Database
- Table `users`: id, email, hashed_password, role (enum), member_id (FK), is_active
- Alembic migration: `002_add_users_table.py`

## Chưa implement
- Quên mật khẩu (reset qua email)
- Admin panel quản lý users
- Rate limiting cho login endpoint
