from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.models.domain import AgentMetadata, ErrorDetail, TaskInput, TaskResult, TaskStatus


def _elapsed_ms(started_at: datetime) -> int:
    now = datetime.now(timezone.utc)
    return int((now - started_at).total_seconds() * 1000)


class BaseAgent(ABC):
    @abstractmethod
    def metadata(self) -> AgentMetadata:
        ...

    @abstractmethod
    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        ...

    async def run(self, task: TaskInput, context: AgentContext) -> TaskResult:
        task_id = uuid.uuid4().hex
        started = datetime.now(timezone.utc)
        try:
            output = await self.execute(task, context)
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                agent_id=self.metadata().agent_id,
                output=output,
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                duration_ms=_elapsed_ms(started),
                traces=context.traces,
            )
        except Exception as exc:
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                agent_id=self.metadata().agent_id,
                error=ErrorDetail(
                    code=type(exc).__name__,
                    message=str(exc),
                    retryable=getattr(exc, "retryable", False),
                ),
                started_at=started,
                completed_at=datetime.now(timezone.utc),
                duration_ms=_elapsed_ms(started),
                traces=context.traces,
            )
