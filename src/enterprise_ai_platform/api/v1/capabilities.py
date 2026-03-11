from fastapi import APIRouter

from enterprise_ai_platform.core.capability_registry import CapabilityRegistry

router = APIRouter(tags=["capabilities"])


@router.get("/capabilities")
def list_capabilities() -> dict[str, object]:
    items: list[dict[str, object]] = []
    for capability in CapabilityRegistry.list_capabilities():
        agent_cls = CapabilityRegistry.resolve(capability)
        agent = agent_cls()
        meta = agent.metadata()
        cap = meta.capabilities[0]
        items.append(
            {
                "name": cap.name,
                "description": cap.description,
                "category": cap.category,
                "agent_id": meta.agent_id,
                "input_schema": cap.input_schema,
                "output_schema": cap.output_schema,
            }
        )
    return {"capabilities": items}
