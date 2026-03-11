from pydantic import BaseModel
from fastapi import APIRouter, Depends

from enterprise_ai_platform.dependencies import get_knowledge_service
from enterprise_ai_platform.services.knowledge_service import KnowledgeService

router = APIRouter(tags=["knowledge"])


class KnowledgeRecord(BaseModel):
    content: str


@router.post("/knowledge")
def add_knowledge(record: KnowledgeRecord, service: KnowledgeService = Depends(get_knowledge_service)) -> dict[str, object]:
    service.add_document({"content": record.content})
    return {"status": "ok"}


@router.get("/knowledge")
def search_knowledge(q: str, service: KnowledgeService = Depends(get_knowledge_service)) -> dict[str, object]:
    return {"results": service.search(q)}
