from __future__ import annotations

from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import TaskInput, TaskResult


class AgentService:
    def __init__(self, context_factory):
        self.context_factory = context_factory

    async def execute(self, task_input: TaskInput) -> TaskResult:
        agent_cls = CapabilityRegistry.resolve(task_input.capability)
        agent = agent_cls()
        context: AgentContext = self.context_factory()
        return await agent.run(task_input, context)
