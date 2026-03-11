from __future__ import annotations

from enterprise_ai_platform.core.capability_graph import CapabilityGraph
from enterprise_ai_platform.core.orchestrator import Orchestrator
from enterprise_ai_platform.models.domain import TaskResult


class TaskService:
    def __init__(self, graph: CapabilityGraph, orchestrator: Orchestrator):
        self.graph = graph
        self.orchestrator = orchestrator

    async def create_task(self, request: str, payload: dict[str, object]) -> tuple[object, TaskResult]:
        plan = await self.graph.resolve(request)
        result = await self.orchestrator.execute_plan(plan, {"request": request, **payload})
        return plan, result
