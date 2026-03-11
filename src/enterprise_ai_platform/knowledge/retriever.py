from __future__ import annotations

from enterprise_ai_platform.knowledge.vector_store import VectorStore


class Retriever:
    def __init__(self, store: VectorStore):
        self.store = store

    def search(self, query: str, top_k: int = 5) -> list[dict[str, object]]:
        return self.store.search(query=query, top_k=top_k)
