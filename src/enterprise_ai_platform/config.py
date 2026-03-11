from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "enterprise-ai-platform"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    host: str = "0.0.0.0"
    port: int = 8088

    database_url: str = "postgresql+asyncpg://user:pass@localhost:5432/platform"
    redis_url: str = "redis://localhost:6379/0"

    llm_provider: str = "openai"
    llm_default_model: str = "gpt-4o"
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: str = ""
    llm_organization: str = ""
    llm_timeout_seconds: int = 60
    llm_max_retries: int = 3

    vector_store_type: str = "chroma"
    chroma_persist_dir: str = "./data/chroma"
    pinecone_api_key: str = ""
    pinecone_index: str = ""
    mcp_servers: dict[str, str] = Field(default_factory=dict)

    embedding_model: str = "text-embedding-3-small"

    jwt_secret: str = "change-me"
    api_keys: list[str] = Field(default_factory=lambda: ["dev-key"])
    api_key_header: str = "X-API-Key"
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])

    otel_endpoint: str = ""
    enable_tracing: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_prefix="PLATFORM_")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
