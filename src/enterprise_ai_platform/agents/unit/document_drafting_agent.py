from __future__ import annotations

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, infer_output_language, trace, try_complete_json
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("document_drafting")
class DocumentDraftingAgent(JSONEchoAgent):
    capability_name = "document_drafting"
    agent_id = "document_drafting_agent"
    name = "Document Drafting Agent"
    description = "Draft enterprise documents"
    category = AgentCategory.DOCUMENT
    timeout_seconds = 180

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        document_type = str(task.payload.get("document_type", "report"))
        topic = str(task.payload.get("topic", "Untitled topic"))
        tone = str(task.payload.get("tone", "formal"))
        outline = task.payload.get("outline", ["Overview", "Details", "Recommendations"])
        headings = [str(item) for item in outline] if isinstance(outline, list) and outline else ["Overview"]
        output_language = infer_output_language(
            topic,
            document_type,
            " ".join(headings),
            requested=str(task.payload.get("output_language", "")),
        )
        llm_result = await try_complete_json(
            context,
            system_prompt=(
                "You draft concise enterprise documents. Return JSON only with keys "
                "title, sections, and word_count. "
                f"Write all natural-language fields in {output_language}."
            ),
            user_prompt=(
                f"Create a {tone} {document_type} about '{topic}'. "
                f"Use this outline: {headings}. Output language: {output_language}."
            ),
            schema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "sections": {"type": "array"},
                    "word_count": {"type": "integer"},
                },
                "required": ["title", "sections", "word_count"],
            },
            max_tokens=1800,
        )
        if llm_result is not None and isinstance(llm_result.get("sections"), list):
            trace(
                context,
                action="document_drafting_llm",
                input_summary=f"type={document_type} topic={topic[:50]}",
                output_summary=f"{len(llm_result['sections'])} sections",
            )
            return llm_result
        sections = [
            {
                "heading": heading,
                "content": (
                    (
                        f"이 {document_type} 섹션은 {topic}에 대한 {heading} 내용을 다룹니다. "
                        f"문서 톤은 {tone}이며 초안 수준의 작업 문서입니다."
                    )
                    if output_language == "ko"
                    else (
                        f"This {document_type} section covers {heading.lower()} for {topic}. "
                        f"The tone is {tone} and the content is intended as an initial working draft."
                    )
                ),
            }
            for heading in headings
        ]
        word_count = sum(len(section["content"].split()) for section in sections)
        trace(
            context,
            action="document_drafting",
            input_summary=f"type={document_type} topic={topic[:50]}",
            output_summary=f"{len(sections)} sections",
        )
        title = f"{topic} {document_type}" if output_language == "ko" else f"{topic.title()} {document_type.title()}"
        return {"title": title, "sections": sections, "word_count": word_count}
