from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, trace
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("proofreading")
class ProofreadingAgent(JSONEchoAgent):
    capability_name = "proofreading"
    agent_id = "proofreading_agent"
    name = "Proofreading Agent"
    description = "Review grammar, style and tone"
    category = AgentCategory.DOCUMENT

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        text = str(task.payload.get("text", ""))
        corrected = " ".join(text.split())
        replacements = {" teh ": " the ", " recieve ": " receive ", " occured ": " occurred "}
        suggestions: list[dict[str, object]] = []
        padded = f" {corrected} "
        for original, replacement in replacements.items():
            if original in padded:
                padded = padded.replace(original, replacement)
                suggestions.append(
                    {
                        "original": original.strip(),
                        "replacement": replacement.strip(),
                        "reason": "Common spelling correction",
                        "category": "spelling",
                    }
                )
        corrected = padded.strip()
        if corrected and corrected[0].islower():
            suggestions.append(
                {
                    "original": corrected[0],
                    "replacement": corrected[0].upper(),
                    "reason": "Sentence should start with a capital letter",
                    "category": "grammar",
                }
            )
            corrected = corrected[0].upper() + corrected[1:]
        trace(
            context,
            action="proofreading",
            input_summary=f"{len(text.split())} words",
            output_summary=f"{len(suggestions)} suggestions",
        )
        return {
            "corrected_text": corrected,
            "suggestions": suggestions,
            "total_changes": len(suggestions),
        }
