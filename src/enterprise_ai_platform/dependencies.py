from __future__ import annotations

from functools import lru_cache

from enterprise_ai_platform import agents  # noqa: F401
from enterprise_ai_platform.agents import unit  # noqa: F401
from enterprise_ai_platform.config import get_settings
from enterprise_ai_platform.core.agent_context import AgentContext
from enterprise_ai_platform.core.capability_graph import CapabilityGraph
from enterprise_ai_platform.core.capability_registry import CapabilityRegistry
from enterprise_ai_platform.core.llm_client import LLMClient
from enterprise_ai_platform.core.orchestrator import Orchestrator
from enterprise_ai_platform.core.tool_manager import ToolManager
from enterprise_ai_platform.knowledge.retriever import Retriever
from enterprise_ai_platform.knowledge.vector_store import VectorStore
from enterprise_ai_platform.services.agent_service import AgentService
from enterprise_ai_platform.services.knowledge_service import KnowledgeService
from enterprise_ai_platform.services.task_service import TaskService
from enterprise_ai_platform.tools.database_tool import DatabaseTool
from enterprise_ai_platform.tools.file_system_tool import FileSystemTool
from enterprise_ai_platform.tools.mcp_connector import MCPConnector


@lru_cache(maxsize=1)
def get_llm_client() -> LLMClient:
    return LLMClient(get_settings())


@lru_cache(maxsize=1)
def get_tool_manager() -> ToolManager:
    manager = ToolManager()
    manager.register(DatabaseTool())
    manager.register(FileSystemTool())
    manager.register(MCPConnector())
    return manager


@lru_cache(maxsize=1)
def get_vector_store() -> VectorStore:
    return VectorStore()


@lru_cache(maxsize=1)
def get_retriever() -> Retriever:
    return Retriever(get_vector_store())


def build_context() -> AgentContext:
    return AgentContext(llm=get_llm_client(), tools=get_tool_manager(), knowledge=get_retriever())


@lru_cache(maxsize=1)
def get_agent_service() -> AgentService:
    return AgentService(context_factory=build_context)


@lru_cache(maxsize=1)
def get_task_service() -> TaskService:
    graph = CapabilityGraph(registry=CapabilityRegistry, llm=get_llm_client())
    orchestrator = Orchestrator(registry=CapabilityRegistry, context_factory=build_context)
    return TaskService(graph=graph, orchestrator=orchestrator)


@lru_cache(maxsize=1)
def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService(get_vector_store())
