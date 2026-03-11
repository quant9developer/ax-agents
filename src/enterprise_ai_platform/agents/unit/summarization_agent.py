from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, summarize_text, trace
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.exceptions import ToolError
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
            "file_path": {"type": "string"},
            "max_length": {"type": "integer"},
            "style": {"type": "string"},
        },
        "required": [],
    }
    output_schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "key_points": {"type": "array", "items": {"type": "string"}},
            "original_length": {"type": "integer"},
            "summary_length": {"type": "integer"},
            "source_path": {"type": ["string", "null"]},
        },
        "required": ["summary", "key_points", "original_length", "summary_length"],
    }

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        text = str(task.payload.get("text", ""))
        file_path = str(task.payload.get("file_path", "")).strip()
        max_length = int(task.payload.get("max_length", 200))
        source_path = ""
        if file_path and context.tools.has_tool("mcp"):
            try:
                mcp_result = await context.tools.invoke(
                    "mcp",
                    {
                        "server": "filesystem",
                        "tool": "read_text",
                        "arguments": {"path": file_path},
                    },
                )
                result_body = mcp_result.get("result", {})
                if isinstance(result_body, dict):
                    mcp_text = str(result_body.get("content", "")).strip()
                    if mcp_text:
                        text = mcp_text
                        source_path = str(result_body.get("path", file_path))
                        trace(
                            context,
                            action="summarization_mcp_filesystem",
                            input_summary=f"Read {file_path}",
                            output_summary=f"Loaded {len(text.split())} words",
                        )
            except (KeyError, ToolError):
                trace(
                    context,
                    action="summarization_mcp_filesystem",
                    input_summary=f"Read {file_path}",
                    output_summary="filesystem mcp unavailable",
                )
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
            "source_path": source_path or None,
        }
