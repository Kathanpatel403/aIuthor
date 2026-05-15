from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/.env — stable regardless of process cwd
_BACKEND_DIR = Path(__file__).resolve().parents[2]
_DEFAULT_ENV_FILE = _BACKEND_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from backend/.env."""

    model_config = SettingsConfigDict(
        env_file=str(_DEFAULT_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    aiuthor_env: Literal["development", "staging", "production"] = Field(
        default="development",
        validation_alias="AIUTHOR_ENV",
    )
    aiuthor_api_prefix: str = Field(default="/api", validation_alias="AIUTHOR_API_PREFIX")
    aiuthor_memory_backend: Literal["memory", "redis"] = Field(
        default="memory",
        validation_alias="AIUTHOR_MEMORY_BACKEND",
        description="memory = in-process store; redis = not wired in Phase 2",
    )

    langchain_tracing_v2: bool = Field(default=False, validation_alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: str | None = Field(default=None, validation_alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="aiuthor", validation_alias="LANGCHAIN_PROJECT")

    # --- Phase 5 agents ---
    anthropic_api_key: str | None = Field(default=None, validation_alias="ANTHROPIC_API_KEY")

    # --- Phase 3 RAG ---
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="OPENAI_EMBEDDING_MODEL",
    )
    pinecone_api_key: str | None = Field(default=None, validation_alias="PINECONE_API_KEY")
    pinecone_index_name: str = Field(default="aiuthor", validation_alias="PINECONE_INDEX_NAME")
    pinecone_rerank_model: str = Field(
        default="cohere-rerank-3.5",
        validation_alias="PINECONE_RERANK_MODEL",
        description="Pinecone Inference rerank model (hosted; uses PINECONE_API_KEY only).",
    )
    tavily_api_key: str | None = Field(default=None, validation_alias="TAVILY_API_KEY")
    rag_dense_top_k: int = Field(default=20, ge=5, le=100, validation_alias="RAG_DENSE_TOP_K")
    rag_bm25_top_k: int = Field(default=20, ge=5, le=100, validation_alias="RAG_BM25_TOP_K")
    rag_rrf_k: int = Field(default=60, ge=1, validation_alias="RAG_RRF_K")
    rag_final_top_n: int = Field(default=5, ge=1, le=20, validation_alias="RAG_FINAL_TOP_N")


@lru_cache
def get_settings() -> Settings:
    return Settings()
