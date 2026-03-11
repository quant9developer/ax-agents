from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, summarize_text, trace
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("summarization")
class SummarizationAgent(JSONEchoAgent):
    capability_name = "summarization"
    agent_id = "summarization_agent"
    name = "Document Summarization Agent"
    description = "Summarize long documents or text"
    category = AgentCategory.DOCUMENT
    timeout_seconds = 120
    input_schema = {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "max_length": {"type": "integer"},
            "style": {"type": "string"},
        },
        "required": ["text"],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "key_points": {"type": "array", "items": {"type": "string"}},
            "original_length": {"type": "integer"},
            "summary_length": {"type": "integer"},
        },
        "required": ["summary", "key_points", "original_length", "summary_length"],
    }

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        text = str(task.payload.get("text", ""))
        max_length = int(task.payload.get("max_length", 200))
        words = text.split()
        summary, key_points = summarize_text(text, max_words=max_length)
        if not summary:
            summary = text[: min(len(text), 200)]
            key_points = [summary] if summary else []
        trace(
            context,
            action="summarization",
            input_summary=f"Summarize text ({len(words)} words)",
            output_summary=f"Generated summary ({len(summary.split())} words)",
        )
        return {
            "summary": summary,
            "key_points": key_points,
            "original_length": len(words),
            "summary_length": len(summary.split()),
        }
