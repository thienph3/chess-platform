---
inclusion: always
---

# Environment — VCC Platform

## Runtime Environment

- OS: Ubuntu 22.04 chạy trong WSL2 (Windows Subsystem for Linux)
- Workspace path: `/home/phthien/workspace/vcc-platform`
- Shell: zsh (Linux shell, không phải PowerShell hay CMD)

## Command Rules

- Dùng Linux commands (bash/zsh syntax), KHÔNG dùng Windows commands.
- Path separator: `/` (forward slash), KHÔNG dùng `\`.
- Khi chạy commands trong subfolder, dùng cwd tương đối: `frontend`, `backend`.
- Package managers: `npm` (frontend), `pip` / `uv` (backend).
- Docker & Docker Compose có sẵn.
