from __future__ import annotations

from pathlib import Path

from enterprise_ai_platform.agents.unit.common import JSONEchoAgent, trace
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.models.domain import AgentCategory, TaskInput


@CapabilityRegistry.register("ocr")
class OCRAgent(JSONEchoAgent):
    capability_name = "ocr"
    agent_id = "ocr_agent"
    name = "OCR Agent"
    description = "Extract text from documents"
    category = AgentCategory.DOCUMENT

    async def execute(self, task: TaskInput, context: AgentContext) -> dict[str, object]:
        file_path = Path(str(task.payload.get("file_path", "")))
        extracted = ""
        if file_path.exists() and file_path.is_file():
            try:
                extracted = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                extracted = f"Binary file detected at {file_path.name}."
        if not extracted:
            extracted = f"OCR placeholder text extracted from {file_path.name or 'document'}."
        trace(
            context,
            action="ocr",
            input_summary=str(file_path),
            output_summary=f"{len(extracted)} chars extracted",
        )
        return {
            "text": extracted.strip(),
            "tables": [],
            "pages": 1,
            "confidence": 0.5 if file_path.exists() else 0.2,
        }
