from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window = timedelta(seconds=window_seconds)
        self.requests: dict[str, list[datetime]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        ip = request.client.host if request.client else "unknown"
        now = datetime.utcnow()
        values = self.requests[ip]
        self.requests[ip] = [dt for dt in values if now - dt < self.window]
        if len(self.requests[ip]) >= self.limit:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
        self.requests[ip].append(now)
        return await call_next(request)
