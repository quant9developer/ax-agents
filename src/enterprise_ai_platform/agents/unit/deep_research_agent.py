from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, summarize_text, top_keywords, trace, try_complete_json
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("deep_research")
class DeepResearchAgent(JSONEchoAgent):
    capability_name = "deep_research"
    agent_id = "deep_research_agent"
    name = "Deep Research Agent"
    description = "Conduct multi-source deep research"
    category = AgentCategory.RESEARCH
    timeout_seconds = 300

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        topic = str(task.payload.get("topic", "")).strip()
        depth = str(task.payload.get("depth", "standard"))
        sources_limit = max(1, int(task.payload.get("sources_limit", 10)))
        knowledge_hits = context.knowledge.search(topic, top_k=sources_limit)
        evidence_text = " ".join(str(item.get("content", item)) for item in knowledge_hits)
        combined = f"{topic}. {evidence_text}".strip()
        llm_result = await try_complete_json(
            context,
            system_prompt=(
                "You are a research synthesis model. Return JSON only with keys "
                "summary, key_insights, supporting_evidence, and confidence."
            ),
            user_prompt=(
                f"Topic: {topic}\nDepth: {depth}\nEvidence:\n{combined[:6000]}\n"
                "Summarize the topic with evidence-backed claims."
            ),
            schema={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "key_insights": {"type": "array"},
                    "supporting_evidence": {"type": "array"},
                    "confidence": {"type": "number"},
                },
                "required": ["summary", "key_insights", "supporting_evidence", "confidence"],
            },
            max_tokens=1800,
        )
        if llm_result is not None and isinstance(llm_result.get("key_insights"), list):
            trace(
                context,
                action="deep_research_llm",
                input_summary=f"topic={topic[:60]} depth={depth}",
                output_summary=f"{len(llm_result['key_insights'])} insights",
            )
            return llm_result
        summary, key_points = summarize_text(combined, max_words=180 if depth == "comprehensive" else 120)
        keyword_pairs = top_keywords(combined, limit=min(5, sources_limit))
        supporting_evidence = [
            {
                "claim": f"{keyword.title()} is relevant to {topic}",
                "source": f"knowledge:{index + 1}",
                "confidence": round(max(0.35, 0.8 - (index * 0.08)), 2),
            }
            for index, (keyword, _count) in enumerate(keyword_pairs)
        ]
        if not supporting_evidence:
            supporting_evidence = [
                {
                    "claim": f"Baseline research summary for {topic}",
                    "source": "generated:local",
                    "confidence": 0.45,
                }
            ]
        trace(
            context,
            action="deep_research",
            input_summary=f"topic={topic[:60]} depth={depth}",
            output_summary=f"{len(supporting_evidence)} evidence items",
        )
        return {
            "summary": summary or f"Local research summary for {topic}.",
            "key_insights": key_points or [f"Research baseline generated for {topic}."],
            "supporting_evidence": supporting_evidence,
            "confidence": round(min(0.95, 0.45 + (0.05 * len(supporting_evidence))), 2),
        }
