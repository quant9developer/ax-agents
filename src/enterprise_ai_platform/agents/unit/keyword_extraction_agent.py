from __future__ import annotations

import re

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, clamp, top_keywords, trace, unique_preserve_order
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("keyword_extraction")
class KeywordExtractionAgent(JSONEchoAgent):
    capability_name = "keyword_extraction"
    agent_id = "keyword_extraction_agent"
    name = "Keyword Extraction Agent"
    description = "Extract keywords and entities"
    category = AgentCategory.LANGUAGE

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        text = str(task.payload.get("text", ""))
        max_keywords = max(1, int(task.payload.get("max_keywords", 10)))
        keyword_counts = top_keywords(text, limit=max_keywords)
        highest = keyword_counts[0][1] if keyword_counts else 1
        keywords = [
            {
                "keyword": keyword,
                "relevance": round(clamp(count / highest, 0.0, 1.0), 2),
            }
            for keyword, count in keyword_counts
        ]
        entity_tokens = unique_preserve_order(re.findall(r"\b[A-Z][a-zA-Z]+\b", text))
        entities = [{"text": token, "type": "other"} for token in entity_tokens[: max_keywords // 2 or 1]]
        trace(
            context,
            action="keyword_extraction",
            input_summary=f"{len(text)} chars",
            output_summary=f"{len(keywords)} keywords",
        )
        return {"keywords": keywords, "entities": entities}
