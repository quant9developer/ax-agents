from __future__ import annotations

import re

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, summarize_text, top_keywords, trace, try_complete_json
from enterprise_ai_platform.core.exceptions import ToolError
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput

HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")


@CapabilityRegistry.register("deep_research")
class DeepResearchAgent(JSONEchoAgent):
    capability_name = "deep_research"
    agent_id = "deep_research_agent"
    name = "Deep Research Agent"
    description = "Conduct multi-source deep research"
    category = AgentCategory.RESEARCH
    timeout_seconds = 300

    @staticmethod
    def _resolve_output_language(task: TaskInput, topic: str) -> str:
        requested = str(task.payload.get("output_language", "")).strip().lower()
        if requested:
            return requested
        if HANGUL_RE.search(topic):
            return "ko"
        return "en"

    @staticmethod
    def _build_sources(
        hits: list[dict[str, object]],
        *,
        output_language: str,
        limit: int,
    ) -> list[dict[str, object]]:
        sources: list[dict[str, object]] = []
        seen: set[str] = set()
        for index, item in enumerate(hits):
            title = str(item.get("title", "")).strip() or (
                f"Source {index + 1}" if output_language != "ko" else f"출처 {index + 1}"
            )
            url = str(item.get("source", item.get("url", ""))).strip() or f"knowledge:{index + 1}"
            if url in seen:
                continue
            seen.add(url)
            snippet = str(item.get("content", item.get("snippet", ""))).strip()
            sources.append(
                {
                    "title": title,
                    "url": url,
                    "snippet": snippet[:280],
                }
            )
            if len(sources) >= limit:
                break
        return sources

    async def _collect_mcp_evidence(
        self,
        context: AgentContext,
        *,
        topic: str,
        depth: str,
        sources_limit: int,
    ) -> list[dict[str, object]]:
        if not context.tools.has_tool("mcp"):
            return []

        query = str(topic).strip()
        try:
            response = await context.tools.invoke(
                "mcp",
                {
                    "server": "browser",
                    "tool": "search",
                    "arguments": {
                        "query": query,
                        "limit": sources_limit,
                    },
                },
            )
        except (KeyError, ToolError):
            trace(
                context,
                action="deep_research_mcp",
                input_summary=f"topic={topic[:60]} depth={depth}",
                output_summary="mcp unavailable",
            )
            return []

        result = response.get("result", {})
        items: list[object]
        if isinstance(result, dict):
            raw_items = result.get("items", result.get("results", []))
            items = raw_items if isinstance(raw_items, list) else []
        elif isinstance(result, list):
            items = result
        else:
            items = []

        evidence: list[dict[str, object]] = []
        for index, item in enumerate(items[:sources_limit]):
            if isinstance(item, dict):
                title = str(item.get("title", "Untitled source")).strip() or "Untitled source"
                snippet = str(item.get("snippet", item.get("content", ""))).strip()
                url = str(item.get("url", item.get("source", f"mcp:{index + 1}"))).strip() or f"mcp:{index + 1}"
            else:
                title = f"MCP source {index + 1}"
                snippet = str(item).strip()
                url = f"mcp:{index + 1}"
            if not snippet:
                snippet = title
            if not snippet:
                continue
            evidence.append(
                {
                    "title": title,
                    "content": snippet,
                    "source": url,
                }
            )

        trace(
            context,
            action="deep_research_mcp",
            input_summary=f"topic={topic[:60]} depth={depth}",
            output_summary=f"{len(evidence)} mcp evidence items",
        )
        return evidence

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        topic = str(task.payload.get("topic", "")).strip()
        depth = str(task.payload.get("depth", "standard"))
        sources_limit = max(1, int(task.payload.get("sources_limit", 10)))
        output_language = self._resolve_output_language(task, topic)
        mcp_hits = await self._collect_mcp_evidence(
            context,
            topic=topic,
            depth=depth,
            sources_limit=sources_limit,
        )
        knowledge_hits = context.knowledge.search(topic, top_k=sources_limit)
        combined_hits = [*mcp_hits, *knowledge_hits]
        evidence_text = " ".join(str(item.get("content", item)) for item in combined_hits)
        combined = f"{topic}. {evidence_text}".strip()
        llm_result = await try_complete_json(
            context,
            system_prompt=(
                "You are a research synthesis model. Return JSON only with keys "
                "summary, key_insights, supporting_evidence, sources, and confidence. "
                f"Write all natural-language fields in {output_language}."
            ),
            user_prompt=(
                f"Topic: {topic}\nDepth: {depth}\nOutput language: {output_language}\nEvidence:\n{combined[:6000]}\n"
                "Summarize the topic with evidence-backed claims."
            ),
            schema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "key_insights": {"type": "array"},
                    "supporting_evidence": {"type": "array"},
                    "sources": {"type": "array"},
                    "confidence": {"type": "number"},
                },
                "required": ["summary", "key_insights", "supporting_evidence", "sources", "confidence"],
            },
            max_tokens=1800,
        )
        if llm_result is not None and isinstance(llm_result.get("key_insights"), list):
            llm_result["sources"] = self._build_sources(
                combined_hits,
                output_language=output_language,
                limit=sources_limit,
            )
            trace(
                context,
                action="deep_research_llm",
                input_summary=f"topic={topic[:60]} depth={depth}",
                output_summary=f"{len(llm_result['key_insights'])} insights",
            )
            return llm_result
        summary, key_points = summarize_text(combined, max_words=180 if depth == "comprehensive" else 120)
        keyword_pairs = top_keywords(combined, limit=min(5, sources_limit))
        if output_language == "ko":
            supporting_evidence = [
                {
                    "claim": f"{keyword}은(는) {topic}과 관련이 있습니다.",
                    "source": (
                        str(combined_hits[index].get("source", f"knowledge:{index + 1}"))
                        if index < len(combined_hits) and isinstance(combined_hits[index], dict)
                        else f"knowledge:{index + 1}"
                    ),
                    "confidence": round(max(0.35, 0.8 - (index * 0.08)), 2),
                }
                for index, (keyword, _count) in enumerate(keyword_pairs)
            ]
        else:
            supporting_evidence = [
                {
                    "claim": f"{keyword.title()} is relevant to {topic}",
                    "source": (
                        str(combined_hits[index].get("source", f"knowledge:{index + 1}"))
                        if index < len(combined_hits) and isinstance(combined_hits[index], dict)
                        else f"knowledge:{index + 1}"
                    ),
                    "confidence": round(max(0.35, 0.8 - (index * 0.08)), 2),
                }
                for index, (keyword, _count) in enumerate(keyword_pairs)
            ]
        if not supporting_evidence:
            supporting_evidence = (
                [
                    {
                        "claim": f"{topic}에 대한 기본 리서치 요약입니다.",
                        "source": "generated:local",
                        "confidence": 0.45,
                    }
                ]
                if output_language == "ko"
                else [
                    {
                        "claim": f"Baseline research summary for {topic}",
                        "source": "generated:local",
                        "confidence": 0.45,
                    }
                ]
            )
        trace(
            context,
            action="deep_research",
            input_summary=f"topic={topic[:60]} depth={depth}",
            output_summary=f"{len(supporting_evidence)} evidence items",
        )
        sources = self._build_sources(
            combined_hits,
            output_language=output_language,
            limit=sources_limit,
        )
        return {
            "summary": (
                summary
                or (f"{topic}에 대한 로컬 리서치 요약입니다." if output_language == "ko" else f"Local research summary for {topic}.")
            ),
            "key_insights": (
                key_points
                or ([f"{topic}에 대한 기본 리서치 인사이트입니다."] if output_language == "ko" else [f"Research baseline generated for {topic}."])
            ),
            "supporting_evidence": supporting_evidence,
            "sources": sources,
            "confidence": round(min(0.95, 0.45 + (0.05 * len(supporting_evidence))), 2),
        }
