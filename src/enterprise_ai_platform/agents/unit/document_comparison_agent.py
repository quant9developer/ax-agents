from __future__ import annotations

from difflib import SequenceMatcher

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, split_sentences, summarize_text, trace
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("document_comparison")
class DocumentComparisonAgent(JSONEchoAgent):
    capability_name = "document_comparison"
    agent_id = "document_comparison_agent"
    name = "Document Comparison Agent"
    description = "Compare two documents"
    category = AgentCategory.DOCUMENT
    timeout_seconds = 180

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        document_a = str(task.payload.get("document_a", ""))
        document_b = str(task.payload.get("document_b", ""))
        sentences_a = split_sentences(document_a)
        sentences_b = split_sentences(document_b)
        differences: list[dict[str, object]] = []
        for index, sentence in enumerate(sentences_a[:5]):
            other = sentences_b[index] if index < len(sentences_b) else ""
            if sentence != other:
                differences.append(
                    {
                        "location": f"sentence_{index + 1}",
                        "type": "modified" if other else "removed",
                        "document_a_text": sentence,
                        "document_b_text": other,
                        "significance": "medium",
                    }
                )
        similarity = SequenceMatcher(None, document_a, document_b).ratio()
        summary, _ = summarize_text(" ".join(item["document_a_text"] for item in differences), max_words=60)
        trace(
            context,
            action="document_comparison",
            input_summary=f"a={len(document_a)} chars b={len(document_b)} chars",
            output_summary=f"{len(differences)} differences",
        )
        return {
            "differences": differences,
            "summary": (
                summary
                or ("Documents are largely similar." if similarity > 0.9 else "Documents differ in several sections.")
            ),
            "similarity_score": round(similarity, 4),
        }
