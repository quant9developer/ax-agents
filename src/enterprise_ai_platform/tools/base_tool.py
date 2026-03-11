from __future__ import annotations

from abc import ABC, abstractmethod

from enterprise_ai_platform.models.domain import ToolDescriptor


class BaseTool(ABC):
    @abstractmethod
    def descriptor(self) -> ToolDescriptor:
        ...

    @abstractmethod
    async def invoke(self, input_data: dict[str, object]) -> dict[str, object]:
        ...
