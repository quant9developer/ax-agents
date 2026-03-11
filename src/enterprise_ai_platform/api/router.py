from fastapi import APIRouter

from enterprise_ai_platform.api.v1.agents import router as agents_router
from enterprise_ai_platform.api.v1.capabilities import router as capabilities_router
from enterprise_ai_platform.api.v1.demo import router as demo_router
from enterprise_ai_platform.api.v1.health import router as health_router
from enterprise_ai_platform.api.v1.knowledge import router as knowledge_router
from enterprise_ai_platform.api.v1.tasks import router as tasks_router
from enterprise_ai_platform.api.v1.tools import router as tools_router

router = APIRouter(prefix="/v1")
router.include_router(health_router)
router.include_router(demo_router)
router.include_router(capabilities_router)
router.include_router(agents_router)
router.include_router(tasks_router)
router.include_router(tools_router)
router.include_router(knowledge_router)
