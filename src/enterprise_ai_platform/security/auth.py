from __future__ import annotations

from fastapi import Header

from enterprise_ai_platform.config import get_settings
from enterprise_ai_platform.core.exceptions import AuthenticationError


def validate_api_key(x_api_key: str | None = Header(default=None)) -> str:
    settings = get_settings()
    if x_api_key and x_api_key in settings.api_keys:
        return "api_key_user"
    raise AuthenticationError("Invalid API key")
