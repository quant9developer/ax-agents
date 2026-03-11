from datetime import datetime, timezone

from fastapi import APIRouter

from enterprise_ai_platform.config import get_settings
from enterprise_ai_platform.dependencies import get_llm_client
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry

router = APIRouter(tags=["health"])
STARTED_AT = datetime.now(timezone.utc)


@router.get("/health")
def health() -> dict[str, object]:
    settings = get_settings()
    llm_info = get_llm_client().provider_info()
    uptime = int((datetime.now(timezone.utc) - STARTED_AT).total_seconds())
    return {
        "status": "healthy",
        "version": settings.app_version,
        "agents_loaded": len(CapabilityRegistry.list_capabilities()),
        "uptime_seconds": uptime,
        "llm": llm_info,
    }
