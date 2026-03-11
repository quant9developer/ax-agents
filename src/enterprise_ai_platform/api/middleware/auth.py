from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from enterprise_ai_platform.config import get_settings


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        public_paths = {"/", "/demo", "/demo/", "/favicon.ico"}
        if request.url.path in public_paths or request.url.path.startswith("/demo/") or request.url.path.endswith("/health"):
            return await call_next(request)
        settings = get_settings()
        api_key = request.headers.get(settings.api_key_header)
        if not api_key or api_key not in settings.api_keys:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": "AUTHENTICATION_ERROR",
                        "message": "Invalid API key",
                        "retryable": False,
                    }
                },
            )
        request.state.user_id = "api_key_user"
        return await call_next(request)
