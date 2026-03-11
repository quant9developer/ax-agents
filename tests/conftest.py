import pytest

from enterprise_ai_platform.dependencies import get_agent_service, get_task_service
from enterprise_ai_platform.services.agent_service import AgentService
from enterprise_ai_platform.services.task_service import TaskService


@pytest.fixture
def agent_service() -> AgentService:
    return get_agent_service()


@pytest.fixture
def task_service() -> TaskService:
    return get_task_service()
