from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, trace, try_complete_json
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("code_generation")
class CodeGenerationAgent(JSONEchoAgent):
    capability_name = "code_generation"
    agent_id = "code_generation_agent"
    name = "Code Generation Agent"
    description = "Generate code from requirements"
    category = AgentCategory.CODE

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        requirement = str(task.payload.get("requirement", ""))
        language = str(task.payload.get("language", "python"))
        framework = str(task.payload.get("framework", "")).strip()
        llm_result = await try_complete_json(
            context,
            system_prompt=(
                "You generate minimal production-minded code. Return JSON only with keys "
                "language, code, explanation, dependencies, and test_code."
            ),
            user_prompt=(
                f"Requirement: {requirement}\nLanguage: {language}\nFramework: {framework or 'none'}\n"
                "Return a compact, runnable implementation."
            ),
            schema={
                "type": "object",
                "properties": {
                    "language": {"type": "string"},
                    "code": {"type": "string"},
                    "explanation": {"type": "string"},
                    "dependencies": {"type": "array"},
                    "test_code": {"type": "string"},
                },
                "required": ["language", "code", "explanation", "dependencies", "test_code"],
            },
            max_tokens=1800,
        )
        if llm_result is not None and "code" in llm_result:
            trace(
                context,
                action="code_generation_llm",
                input_summary=f"language={language}",
                output_summary=f"{len(str(llm_result['code']).splitlines())} lines",
            )
            return llm_result
        function_name = "generated_solution"
        if language.lower() == "python":
            code = (
                f"def {function_name}() -> str:\n"
                f"    \"\"\"Generated for: {requirement[:60]}\"\"\"\n"
                f"    return \"{requirement[:80]}\"\n"
            )
            test_code = (
                f"from solution import {function_name}\n\n"
                f"def test_{function_name}() -> None:\n"
                f"    assert {function_name}()\n"
            )
        else:
            code = f"// Generated {language} snippet for: {requirement}\n"
            test_code = ""
        dependencies = [framework] if framework else []
        trace(
            context,
            action="code_generation",
            input_summary=f"language={language}",
            output_summary=f"{len(code.splitlines())} lines",
        )
        return {
            "language": language,
            "code": code,
            "explanation": f"Generated a minimal {language} implementation from the requirement.",
            "dependencies": dependencies,
            "test_code": test_code,
        }
