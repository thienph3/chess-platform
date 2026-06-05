---
inclusion: always
---

# UI Conventions — VCC Platform

## MUI Theme

- Use a custom MUI theme defined in `src/theme/index.ts`.
- Primary color: Vinamilk Green (#00653E).
- Secondary color: Cream (#F5E6C8).
- Accent: Warm Yellow (#FFB800).
- Background: Off-white (#FAFAF7) for pages, white for cards.
- Typography: Nunito font family (fallback: Inter).
- Border radius: 12px default for cards, 24px for buttons.
- Spacing unit: 8px (MUI default).

## Layout

- Use MUI `Box`, `Container`, `Stack`, `Grid` for layout — no raw div with inline styles.
- Max content width: 1200px (lg breakpoint).
- Sidebar navigation for desktop, bottom nav for mobile.
- Responsive breakpoints: xs (0), sm (600), md (900), lg (1200), xl (1536).

## Components

- Prefer MUI components over custom implementations.
- Use `DataGrid` (MUI X) for tables with sorting/filtering/pagination.
- Use `Dialog` for modals, `Drawer` for side panels.
- Use `Skeleton` for loading states, never blank screens.
- Use `Alert` / `Snackbar` for notifications (success, error, info).
- Form inputs: use `TextField`, `Select`, `Autocomplete` with proper labels and helper text.

## Forms

- Use React Hook Form + Yup/Zod for validation.
- Show inline validation errors below fields.
- Disable submit button while loading.
- Show success/error feedback via Snackbar after submission.

## Icons

- Use `@mui/icons-material` for consistency.
- Icon size: 20px for inline, 24px for buttons, 40px for empty states.

## Accessibility

- All interactive elements must be keyboard accessible.
- Use semantic HTML (headings hierarchy, landmarks).
- Images/icons must have alt text or aria-label.
- Color contrast ratio: minimum 4.5:1 for text.
- Focus indicators must be visible.

## Vietnamese Language

- All user-facing text in Vietnamese.
- Use consistent terminology:
  - Member = Thành viên
  - Tournament = Giải đấu
  - Match = Ván đấu
  - Rating = Hệ số ELO
  - Leaderboard = Bảng xếp hạng
  - Finance = Tài chính
  - Chess = Cờ vua
  - Xiangqi = Cờ tướng
  - Go = Cờ vây

## Game Page Layout (theo chess.com style)

- Layout 3 cột: [Eval Bar] | [Board Area] | [Side Panel]
- Board area:
  - Player bar phía trên board: avatar + tên + rating + đồng hồ (căn phải)
  - Board ở giữa (vuông, responsive)
  - Player bar phía dưới board: avatar + tên + rating + đồng hồ (căn phải)
  - Player bar active highlight nhẹ
- Side panel (bên phải board):
  - Move list: 2 cột (trắng | đen), 1 cặp per row, scroll
  - Action buttons dưới move list: đầu hàng, xin hòa, phân tích
  - Game result hiển thị overlay trên board khi kết thúc
- Eval bar (trái board): thanh dọc gradient trắng/đen, chiều cao = board
- Đồng hồ: nền đậm khi active, font monospace lớn, đỏ khi < 30s
- Move list: font monospace, highlight nước vừa đi, auto-scroll xuống cuối
