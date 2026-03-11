from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Metrics:
    agent_executions_total: dict[str, int] = field(default_factory=dict)
    llm_calls_total: dict[str, int] = field(default_factory=dict)
    tool_invocations_total: dict[str, int] = field(default_factory=dict)
    active_tasks: int = 0

    def inc_agent(self, key: str) -> None:
        self.agent_executions_total[key] = self.agent_executions_total.get(key, 0) + 1
