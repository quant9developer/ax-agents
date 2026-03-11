from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import uuid

from enterprise_ai_platform.core.capability_graph import ExecutionPlan
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import ErrorDetail, TaskInput, TaskResult, TaskStatus


class Orchestrator:
    def __init__(self, registry: type[CapabilityRegistry], context_factory):
        self.registry = registry
        self.context_factory = context_factory

    async def execute_plan(self, plan: ExecutionPlan, initial_input: dict[str, object]) -> TaskResult:
        started_at = datetime.now(timezone.utc)
        task_id = uuid.uuid4().hex
        if not plan.steps:
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                agent_id="orchestrator",
                error=ErrorDetail(code="EMPTY_PLAN", message="No steps in execution plan", retryable=False),
                started_at=started_at,
                completed_at=datetime.now(timezone.utc),
                duration_ms=0,
            )

        completed: dict[int, dict[str, object]] = {}
        pending = {step.step_number: step for step in plan.steps}
        deps = {step.step_number: set(step.depends_on) for step in plan.steps}
        traces = []

        while pending:
            ready = [n for n, dep in deps.items() if not dep and n in pending]
            if not ready:
                return TaskResult(
                    task_id=task_id,
                    status=TaskStatus.FAILED,
                    agent_id="orchestrator",
                    error=ErrorDetail(code="PLAN_DEADLOCK", message="Cyclic or invalid dependencies", retryable=False),
                    started_at=started_at,
                    completed_at=datetime.now(timezone.utc),
                    duration_ms=int((datetime.now(timezone.utc) - started_at).total_seconds() * 1000),
                    traces=traces,
                )
            batch = [pending[s] for s in ready]
            results = await asyncio.gather(*[self._run_step(step, initial_input, completed) for step in batch])
            for step_num, result in results:
                traces.extend(result.traces)
                if result.status != TaskStatus.COMPLETED or result.output is None:
                    return TaskResult(
                        task_id=task_id,
                        status=TaskStatus.FAILED,
                        agent_id="orchestrator",
                        error=result.error,
                        started_at=started_at,
                        completed_at=datetime.now(timezone.utc),
                        duration_ms=int((datetime.now(timezone.utc) - started_at).total_seconds() * 1000),
                        traces=traces,
                    )
                completed[step_num] = result.output
                pending.pop(step_num, None)
                for dep_set in deps.values():
                    dep_set.discard(step_num)

        final_step = max(completed.keys())
        return TaskResult(
            task_id=task_id,
            status=TaskStatus.COMPLETED,
            agent_id="orchestrator",
            output=completed[final_step],
            started_at=started_at,
            completed_at=datetime.now(timezone.utc),
            duration_ms=int((datetime.now(timezone.utc) - started_at).total_seconds() * 1000),
            traces=traces,
        )

    async def _run_step(
        self,
        step,
        initial_input: dict[str, object],
        completed: dict[int, dict[str, object]],
    ) -> tuple[int, TaskResult]:
        agent_cls = self.registry.resolve(step.capability)
        agent = agent_cls()
        payload: dict[str, object] = {}
        for target, source in step.input_mapping.items():
            payload[target] = self._resolve_mapping(source, initial_input, completed)
        context = self.context_factory()
        result = await agent.run(TaskInput(capability=step.capability, payload=payload), context)
        return step.step_number, result

    @staticmethod
    def _resolve_mapping(
        source: str,
        initial_input: dict[str, object],
        completed: dict[int, dict[str, object]],
    ) -> object:
        if source.startswith("user_input."):
            key = source.removeprefix("user_input.")
            return initial_input.get(key)
        if source.startswith("step_"):
            left, _, key = source.partition(".output.")
            step_num = int(left.replace("step_", ""))
            return completed.get(step_num, {}).get(key)
        return source
