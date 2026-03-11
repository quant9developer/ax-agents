import pytest

from enterprise_ai_platform.core.capability_graph import CapabilityGraph
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.core.llm_client import LLMClient


@pytest.mark.asyncio
async def test_resolve_single_step() -> None:
    from enterprise_ai_platform.agents import unit  # noqa: F401

    graph = CapabilityGraph(registry=CapabilityRegistry, llm=LLMClient())
    plan = await graph.resolve("Please summarize this document")
    assert len(plan.steps) >= 1
