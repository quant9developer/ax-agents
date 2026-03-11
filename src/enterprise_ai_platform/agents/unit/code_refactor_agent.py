from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, clamp, infer_output_language, trace, try_complete_json
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("code_refactor")
class CodeRefactorAgent(JSONEchoAgent):
    capability_name = "code_refactor"
    agent_id = "code_refactor_agent"
    name = "Code Refactor Agent"
    description = "Explain and refactor code"
    category = AgentCategory.CODE

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        code = str(task.payload.get("code", ""))
        action = str(task.payload.get("action", "refactor"))
        output_language = infer_output_language(
            code,
            action,
            requested=str(task.payload.get("output_language", "")),
        )
        llm_result = await try_complete_json(
            context,
            system_prompt=(
                "You analyze and refactor source code. Return JSON only with keys "
                "refactored_code, explanation, improvements, and quality_score. "
                f"Write explanatory fields in {output_language}. Keep code in its source language."
            ),
            user_prompt=(
                f"Action: {action}\nCode:\n{code[:7000]}\n"
                f"Provide the requested analysis or refactor. Output language: {output_language}."
            ),
            schema={
                "type": "object",
                "properties": {
                    "refactored_code": {"type": "string"},
                    "explanation": {"type": "string"},
                    "improvements": {"type": "array"},
                    "quality_score": {"type": "number"},
                },
                "required": ["refactored_code", "explanation", "improvements", "quality_score"],
            },
            max_tokens=1800,
        )
        if llm_result is not None and "explanation" in llm_result:
            trace(
                context,
                action="code_refactor_llm",
                input_summary=f"{len(code.splitlines())} lines",
                output_summary=f"{len(llm_result.get('improvements', []))} improvements",
            )
            return llm_result
        refactored = code.replace("\t", "    ").strip()
        explanation = (
            f"가독성과 형식 일관성에 초점을 맞춰 {action} 작업을 수행했습니다."
            if output_language == "ko"
            else f"Performed a lightweight {action} pass focused on readability and formatting."
        )
        improvements = []
        if "print(" in code:
            improvements.append(
                {
                    "description": (
                        "print 문을 로깅으로 대체하는 것을 고려하세요."
                        if output_language == "ko"
                        else "Consider replacing print statements with logging."
                    ),
                    "severity": "medium",
                }
            )
        if "==" in code and "None" in code:
            improvements.append(
                {
                    "description": (
                        "'is None' 검사를 사용하면 더 명확합니다."
                        if output_language == "ko"
                        else "Use 'is None' checks for clarity."
                    ),
                    "severity": "low",
                }
            )
        quality_score = clamp(0.55 + (0.1 * len(improvements)), 0.0, 1.0)
        trace(
            context,
            action="code_refactor",
            input_summary=f"{len(code.splitlines())} lines",
            output_summary=f"{len(improvements)} improvements",
        )
        return {
            "refactored_code": refactored if action in {"refactor", "optimize"} else "",
            "explanation": explanation,
            "improvements": improvements,
            "quality_score": round(quality_score, 2),
        }
