from __future__ import annotations

from enterprise_ai_platform.core.base_agent import BaseAgent
from enterprise_ai_platform.core.exceptions import CapabilityNotFoundError


class CapabilityRegistry:
    _registry: dict[str, type[BaseAgent]] = {}

    @classmethod
    def register(cls, capability_name: str):
        def wrapper(agent_cls: type[BaseAgent]) -> type[BaseAgent]:
            cls._registry[capability_name] = agent_cls
            return agent_cls

        return wrapper

    @classmethod
    def resolve(cls, capability: str) -> type[BaseAgent]:
        if capability not in cls._registry:
            raise CapabilityNotFoundError(
                f"No agent registered for capability '{capability}'. "
                f"Available: {list(cls._registry.keys())}"
            )
        return cls._registry[capability]

    @classmethod
    def list_capabilities(cls) -> list[str]:
        return sorted(cls._registry.keys())

    @classmethod
    def clear(cls) -> None:
        cls._registry.clear()
