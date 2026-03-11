from __future__ import annotations

from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput
from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, clamp, trace, words


@CapabilityRegistry.register("classification")
class ClassificationAgent(JSONEchoAgent):
    capability_name = "classification"
    agent_id = "classification_agent"
    name = "Category Classification Agent"
    description = "Classify text into categories"
    category = AgentCategory.CLASSIFICATION
    timeout_seconds = 60

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        text = str(task.payload.get("text", ""))
        categories = [str(c) for c in task.payload.get("categories", [])]
        if not categories:
            categories = ["general"]
        text_terms = set(words(text))
        scores: list[dict[str, object]] = []
        best = categories[0]
        best_score = -1.0
        for index, category in enumerate(categories):
            category_terms = set(words(category))
            overlap = len(text_terms & category_terms)
            score = 0.35 + (0.25 * overlap) + max(0.0, 0.15 - (index * 0.03))
            score = clamp(score, 0.0, 1.0)
            scores.append({"category": category, "confidence": round(score, 2)})
            if score > best_score:
                best = category
                best_score = score
        trace(
            context,
            action="classification",
            input_summary=f"{len(text)} chars",
            output_summary=f"category={best}",
        )
        return {
            "category": best,
            "confidence": round(best_score, 2),
            "all_scores": scores,
        }
