import pytest

from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_graph import ExecutionPlan, ExecutionStep
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.core.orchestrator import Orchestrator
from enterprise_ai_platform.core.tool_manager import ToolManager
from enterprise_ai_platform.knowledge.retriever import Retriever
from enterprise_ai_platform.knowledge.vector_store import VectorStore
from enterprise_ai_platform.models.domain import TaskStatus


def context_factory() -> AgentContext:
    return AgentContext(llm=LLMClient(), tools=ToolManager(), knowledge=Retriever(VectorStore()))


@pytest.mark.asyncio
async def test_orchestrator_executes_plan() -> None:
    from enterprise_ai_platform.agents import unit  # noqa: F401

    plan = ExecutionPlan(
        steps=[ExecutionStep(step_number=1, capability="summarization", input_mapping={"text": "user_input.request"})],
        original_request="summarize",
    )
    result = await Orchestrator(CapabilityRegistry, context_factory).execute_plan(plan, {"request": "hello world"})
    assert result.status == TaskStatus.COMPLETED
