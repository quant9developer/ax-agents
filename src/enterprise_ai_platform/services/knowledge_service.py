from __future__ import annotations

from enterprise_ai_platform.knowledge.vector_store import VectorStore


class KnowledgeService:
    def __init__(self, store: VectorStore):
        self.store = store

    def add_document(self, doc: dict[str, object]) -> None:
        self.store.add(doc)

    def search(self, query: str) -> list[dict[str, object]]:
        return self.store.search(query)
