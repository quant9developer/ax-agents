from __future__ import annotations

from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput
from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, trace, try_complete_json


@CapabilityRegistry.register("translation")
class TranslationAgent(JSONEchoAgent):
    capability_name = "translation"
    agent_id = "translation_agent"
    name = "Translation Agent"
    description = "Translate text across languages"
    category = AgentCategory.LANGUAGE
    _phrasebook = {
        ("en", "ko"): {"hello": "안녕하세요", "thank you": "감사합니다", "goodbye": "안녕히 가세요"},
        ("en", "es"): {"hello": "hola", "thank you": "gracias", "goodbye": "adios"},
        ("en", "fr"): {"hello": "bonjour", "thank you": "merci", "goodbye": "au revoir"},
    }

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        text = str(task.payload.get("text", ""))
        source = str(task.payload.get("source_language", "auto"))
        target = str(task.payload.get("target_language", "en"))
        normalized_source = "en" if source == "auto" else source
        llm_result = await try_complete_json(
            context,
            system_prompt=(
                "You translate text accurately. Return JSON only with keys "
                "translated_text, source_language, target_language, and word_count."
            ),
            user_prompt=(
                f"Translate this text from {source} to {target}:\n{text}\n"
                "Preserve the original meaning and formatting."
            ),
            schema={
                "type": "object",
                "properties": {
                    "translated_text": {"type": "string"},
                    "source_language": {"type": "string"},
                    "target_language": {"type": "string"},
                    "word_count": {"type": "integer"},
                },
                "required": ["translated_text", "source_language", "target_language", "word_count"],
            },
            max_tokens=1200,
        )
        if llm_result is not None and "translated_text" in llm_result:
            trace(
                context,
                action="translation_llm",
                input_summary=f"{normalized_source}->{target}",
                output_summary="translated",
            )
            return llm_result
        translated = text
        phrasebook = self._phrasebook.get((normalized_source, target), {})
        for original, replacement in phrasebook.items():
            translated = translated.replace(original, replacement)
            translated = translated.replace(original.title(), replacement)
        if translated == text:
            translated = f"[{target}] {text}"
        trace(
            context,
            action="translation",
            input_summary=f"{normalized_source}->{target}",
            output_summary="translated",
        )
        return {
            "translated_text": translated,
            "source_language": normalized_source,
            "target_language": target,
            "word_count": len(text.split()),
        }
