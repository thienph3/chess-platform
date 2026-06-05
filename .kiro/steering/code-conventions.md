---
inclusion: always
---

# Code Conventions — VCC Platform

## General

- Language: English for code, Vietnamese for user-facing text and comments where helpful.
- Line length: max 120 characters.
- Use UTF-8 encoding everywhere.
- No unused imports or dead code.

## File Size Limits

- **Backend (.py)**: Tối đa 200 LOC/file. Nếu vượt, tách thành file nhỏ hơn.
- **Frontend components (.tsx)**: Tối đa 150 LOC/file. Tách presenter/container nếu vượt.
- **Frontend hooks/utils (.ts)**: Tối đa 100 LOC/file.
- **Test files**: Tối đa 300 LOC/file (cho phép dài hơn vì test cases).
- Nếu một function dài hơn 40 dòng, cân nhắc tách thành helper functions.

## Backend (Python / FastAPI)

### Structure (Modular Monolith)

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry
│   ├── core/                # Config, security, dependencies
│   ├── modules/             # Feature modules
│   │   ├── members/
│   │   ├── tournaments/
│   │   ├── ratings/
│   │   └── finance/
│   ├── shared/              # Shared utilities, base classes
│   └── db/                  # Database engine, session, migrations
├── tests/
├── alembic/
├── pyproject.toml
└── Dockerfile
```

### Design Patterns

- **Repository Pattern**: Each module has a `repository.py` for DB access.
- **Service Layer**: Business logic lives in `service.py`, not in routes.
- **Schema Separation**: Use Pydantic models — `schemas.py` for request/response, `models.py` for SQLAlchemy ORM.
- **Dependency Injection**: Use FastAPI's `Depends()` for services, repos, DB sessions.

### Naming

- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- API routes: `kebab-case` (e.g., `/api/v1/club-members`)

### API Conventions

- Prefix all routes with `/api/v1/`.
- Use standard HTTP methods: GET (list/detail), POST (create), PUT (full update), PATCH (partial), DELETE.
- Return consistent response envelope:
  ```json
  { "data": ..., "message": "...", "errors": null }
  ```
- Use HTTP status codes correctly (201 for create, 204 for delete, 422 for validation).
- Pagination: `?page=1&page_size=20`, response includes `total`, `page`, `page_size`.

### Error Handling

- Custom exception classes in `core/exceptions.py`.
- Global exception handler middleware.
- Never expose stack traces in production.

### Database

- ORM: SQLAlchemy 2.0 (async).
- Migrations: Alembic.
- All models inherit from a shared `Base` with `id`, `created_at`, `updated_at`.
- Use UUID as primary key.

### Testing

- Framework: pytest + httpx (async).
- Test files mirror module structure in `tests/`.

## Frontend (React + MUI)

### Structure

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── api/                 # API client, hooks
│   ├── components/          # Shared/reusable components
│   ├── features/            # Feature modules (pages + logic)
│   │   ├── members/
│   │   ├── tournaments/
│   │   ├── ratings/
│   │   └── finance/
│   ├── hooks/               # Custom hooks
│   ├── theme/               # MUI theme customization
│   ├── types/               # TypeScript types
│   └── utils/               # Helpers
├── public/
├── package.json
├── tsconfig.json
├── vite.config.ts
└── Dockerfile
```

### Design Patterns

- **Feature-based modules**: Each feature folder contains its pages, components, hooks, and types.
- **Container/Presenter**: Separate data-fetching logic (container) from UI rendering (presenter).
- **Custom hooks**: Encapsulate API calls and state logic in hooks (e.g., `useMembers()`).
- **Centralized API layer**: Use axios instance with interceptors in `api/client.ts`.

### Naming

- Files: `PascalCase.tsx` for components, `camelCase.ts` for utilities/hooks.
- Components: `PascalCase`
- Hooks: `useCamelCase`
- Types/Interfaces: `PascalCase` with `I` prefix for interfaces (e.g., `IMember`).
- Constants: `UPPER_SNAKE_CASE`

### TypeScript

- Strict mode enabled.
- No `any` — use proper types or `unknown`.
- Define API response types matching backend schemas.

### State Management

- Server state: TanStack Query (React Query).
- Local/UI state: React useState/useReducer.
- No Redux unless complexity demands it.

### Testing

- Framework: Vitest + React Testing Library.
- Test files co-located with components: `Component.test.tsx`.
