from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, trace, unique_preserve_order
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("web_search")
class WebSearchAgent(JSONEchoAgent):
    capability_name = "web_search"
    agent_id = "web_search_agent"
    name = "Web Search Agent"
    description = "Search web content"
    category = AgentCategory.RESEARCH
    timeout_seconds = 60

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        query = str(task.payload.get("query", "")).strip()
        max_results = max(1, min(int(task.payload.get("max_results", 5)), 20))
        include_snippets = bool(task.payload.get("include_snippets", True))
        query_terms = unique_preserve_order(part.lower() for part in query.split() if part)
        knowledge_hits = context.knowledge.search(query, top_k=max_results)
        results: list[dict[str, object]] = []

        for index, item in enumerate(knowledge_hits, start=1):
            content = str(item.get("content", item))
            results.append(
                {
                    "title": f"Knowledge result {index}: {query[:40] or 'search'}",
                    "url": f"https://knowledge.local/{index}",
                    "snippet": content[:180] if include_snippets else "",
                    "relevance_score": round(max(0.4, 1.0 - ((index - 1) * 0.1)), 2),
                }
            )

        while len(results) < max_results:
            index = len(results) + 1
            keyword = query_terms[(index - 1) % len(query_terms)] if query_terms else "general"
            snippet = f"Derived local result for '{keyword}' related to '{query}'." if include_snippets else ""
            results.append(
                {
                    "title": f"{keyword.title()} insight {index}",
                    "url": f"https://search.local/{keyword}/{index}",
                    "snippet": snippet,
                    "relevance_score": round(max(0.2, 0.95 - ((index - 1) * 0.12)), 2),
                }
            )

        trace(
            context,
            action="web_search",
            input_summary=f"query={query[:60]}",
            output_summary=f"{len(results)} results",
        )
        return {"results": results[:max_results], "query_used": query}
