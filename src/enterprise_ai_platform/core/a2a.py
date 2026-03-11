from __future__ import annotations

from datetime import datetime, timezone
import uuid

from pydantic import BaseModel, Field

from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.core.event_bus import EventBus
from enterprise_ai_platform.models.domain import TaskInput, TaskResult
from enterprise_ai_platform.models.events import EventType, PlatformEvent
from enterprise_ai_platform.services.agent_service import AgentService


class A2ARequest(BaseModel):
    sender_agent_id: str = "external"
    receiver_agent_id: str
    capability: str
    payload: dict[str, object]
    config: dict[str, object] = Field(default_factory=dict)
    context: dict[str, object] = Field(default_factory=dict)


class A2AService:
    def __init__(self, agent_service: AgentService, event_bus: EventBus) -> None:
        self.agent_service = agent_service
        self.event_bus = event_bus

    def list_agents(self) -> list[dict[str, object]]:
        agents: list[dict[str, object]] = []
        for capability in CapabilityRegistry.list_capabilities():
            agent_cls = CapabilityRegistry.resolve(capability)
            metadata = agent_cls().metadata()
            agents.append(
                {
                    "agent_id": metadata.agent_id,
                    "capability": capability,
                    "name": metadata.name,
                    "category": metadata.category,
                    "description": metadata.description,
                }
            )
        return agents

    async def invoke(self, request: A2ARequest) -> TaskResult:
        correlation_id = uuid.uuid4().hex
        receiver_cls = CapabilityRegistry.resolve(request.capability)
        receiver_metadata = receiver_cls().metadata()
        if receiver_metadata.agent_id != request.receiver_agent_id:
            available = {
                agent["agent_id"]: agent["capability"] for agent in self.list_agents()
            }
            raise KeyError(
                f"receiver_agent_id '{request.receiver_agent_id}' does not serve capability "
                f"'{request.capability}'. Available mapping: {available}"
            )

        await self.event_bus.publish(
            PlatformEvent(
                event_id=uuid.uuid4().hex,
                event_type=EventType.AGENT_TO_AGENT_REQUESTED,
                timestamp=datetime.now(timezone.utc),
                payload=request.model_dump(),
                source=request.sender_agent_id,
                correlation_id=correlation_id,
            )
        )

        result = await self.agent_service.execute(
            TaskInput(
                capability=request.capability,
                payload=request.payload,
                config=request.config,
                context={**request.context, "sender_agent_id": request.sender_agent_id},
            )
        )

        await self.event_bus.publish(
            PlatformEvent(
                event_id=uuid.uuid4().hex,
                event_type=EventType.AGENT_TO_AGENT_COMPLETED,
                timestamp=datetime.now(timezone.utc),
                payload={
                    "sender_agent_id": request.sender_agent_id,
                    "receiver_agent_id": request.receiver_agent_id,
                    "capability": request.capability,
                    "task_id": result.task_id,
                    "status": result.status,
                },
                source=request.receiver_agent_id,
                correlation_id=correlation_id,
            )
        )
        return result
