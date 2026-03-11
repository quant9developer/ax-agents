from __future__ import annotations

from dataclasses import dataclass, field

from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.models.domain import TraceEntry

if False:  # pragma: no cover
    from enterprise_ai_platform.core.tool_manager import ToolManager
    from enterprise_ai_platform.knowledge.retriever import Retriever


@dataclass
class AgentContext:
    llm: LLMClient
    tools: "ToolManager"
    knowledge: "Retriever"
    config: dict[str, object] = field(default_factory=dict)
    traces: list[TraceEntry] = field(default_factory=list)
    correlation_id: str = ""
    user_id: str | None = None
    tenant_id: str | None = None

    def add_trace(
        self,
        step: int,
        action: str,
        input_summary: str,
        output_summary: str,
        duration_ms: int,
        **metadata: object,
    ) -> None:
        self.traces.append(
            TraceEntry(
                step=step,
                action=action,
                input_summary=input_summary,
                output_summary=output_summary,
                duration_ms=duration_ms,
                metadata=metadata,
            )
        )
