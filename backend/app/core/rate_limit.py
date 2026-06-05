"""Simple in-memory rate limiter middleware for FastAPI."""
import time
from collections import defaultdict

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limit middleware — limits requests per IP per endpoint pattern."""

    def __init__(self, app, rate_limits: dict[str, tuple[int, int]] | None = None):
        """
        Args:
            rate_limits: dict mapping path prefix to (max_requests, window_seconds).
                         e.g. {"/api/v1/auth/login": (5, 60)} = 5 requests per 60s
        """
        super().__init__(app)
        self.rate_limits = rate_limits or {}
        self.requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        # Skip preflight CORS requests
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip rate limiting in test mode
        if getattr(request.app.state, "testing", False):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        path = request.url.path

        # Tìm rate limit rule phù hợp
        limit_config = None
        for prefix, config in self.rate_limits.items():
            if path.startswith(prefix):
                limit_config = config
                break

        if not limit_config:
            return await call_next(request)

        max_requests, window = limit_config
        key = f"{client_ip}:{path}"
        now = time.time()

        # Xóa requests cũ ngoài window
        self.requests[key] = [t for t in self.requests[key] if now - t < window]

        if len(self.requests[key]) >= max_requests:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "data": None,
                    "message": "Quá nhiều yêu cầu. Vui lòng thử lại sau.",
                    "errors": None,
                },
            )

        self.requests[key].append(now)
        return await call_next(request)
