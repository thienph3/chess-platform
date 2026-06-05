---
inclusion: always
---

# Design Patterns — VCC Platform

## Architecture Overview

- **Modular Monolith** for backend — modules are logically separated but deployed as one unit.
- **SPA** for frontend — single-page app communicating via REST API.
- Backend and frontend are fully decoupled, communicate only through API contracts.
- **Analysis Services** (Chess/Xiangqi/Go) — separate containers running engine binaries.
  - Responsible for: move validation, game analysis, PGN export.
  - Backend calls them via HTTP (validation_client.py).
  - Backend does NOT contain game logic — it's a stateless relay + state holder.

## Backend Patterns

### Module Structure

Each module (`members`, `tournaments`, `ratings`, `finance`) follows:

```
modules/<name>/
├── __init__.py
├── router.py          # FastAPI router (thin, delegates to service)
├── service.py         # Business logic
├── repository.py      # Database queries (SQLAlchemy)
├── models.py          # ORM models
├── schemas.py         # Pydantic request/response schemas
├── dependencies.py    # Module-specific DI providers
└── exceptions.py      # Module-specific exceptions (optional)
```

### Key Principles

1. **Router → Service → Repository**: Never skip layers.
2. **No cross-module DB access**: Modules communicate through services, not by importing each other's models directly.
3. **DTOs at boundaries**: Always convert between ORM models and Pydantic schemas at the service layer.
4. **Async all the way**: Use async/await for DB operations and route handlers.
5. **Configuration via environment**: Use pydantic-settings for config, never hardcode secrets.

### Error Flow

```
Router catches HTTP exceptions
  → Service raises domain exceptions
    → Repository raises DB exceptions (wrapped)
```

### Database Patterns

- **Unit of Work**: Use SQLAlchemy async session as unit of work, commit in service layer.
- **Soft Delete**: Use `is_deleted` flag + `deleted_at` timestamp instead of hard delete.
- **Audit Fields**: All models have `created_at`, `updated_at`, `created_by`.

## Frontend Patterns

### Data Flow

```
API Client (axios) → React Query Hook → Container Component → Presenter Component
```

### Feature Module Structure

```
features/<name>/
├── pages/             # Route-level components
├── components/        # Feature-specific components
├── hooks/             # Data fetching & logic hooks
├── types.ts           # Feature-specific types
└── index.ts           # Public exports
```

### Key Principles

1. **Hooks for logic**: All API calls and complex state go in custom hooks.
2. **Components are pure UI**: Presenter components receive props, render UI, emit events.
3. **Colocation**: Keep related code together in feature folders.
4. **Lazy loading**: Use React.lazy() for feature pages (code splitting by route).
5. **Error boundaries**: Wrap each feature route with an error boundary.

### API Integration

- One axios instance in `api/client.ts` with base URL and interceptors.
- Each feature has an `api.ts` file defining endpoint functions.
- React Query hooks wrap these functions with caching, refetching, and error handling.

### Routing

- Use React Router v6 with nested routes.
- Route structure mirrors feature modules.
- Protected routes via auth wrapper component.

## Shared Conventions

### Environment Management

- `.env` files for local config (never committed).
- `.env.example` as template (committed).
- Docker Compose for local development (DB, backend, frontend).

### Git Workflow

- Branch naming: `feature/<module>-<description>`, `fix/<description>`.
- Commit messages: conventional commits (`feat:`, `fix:`, `refactor:`, `docs:`).
- PR per feature/fix, squash merge to main.
