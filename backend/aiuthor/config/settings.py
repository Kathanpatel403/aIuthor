from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/.env — stable regardless of process cwd
_BACKEND_DIR = Path(__file__).resolve().parents[2]
_REPO_ROOT = Path(__file__).resolve().parents[3]
_ENV_FILES: tuple[str, ...] = tuple(
    str(p) for p in (_REPO_ROOT / ".env", _BACKEND_DIR / ".env") if p.is_file()
)


class Settings(BaseSettings):
    """Application settings from OS env, then repo-root .env, then backend/.env."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILES or None,
        env_file_encoding="utf-8-sig",
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
    aiuthor_memory_persist: bool = Field(
        default=True,
        validation_alias="AIUTHOR_MEMORY_PERSIST",
        description="When true, memory store snapshots are written under memory_data/ (survives server restarts).",
    )
    aiuthor_memory_data_dir: str | None = Field(
        default=None,
        validation_alias="AIUTHOR_MEMORY_DATA_DIR",
        description="Override directory for memory JSON snapshots (default: <repo>/memory_data).",
    )

    langchain_tracing_v2: bool = Field(default=False, validation_alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: str | None = Field(default=None, validation_alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="aiuthor", validation_alias="LANGCHAIN_PROJECT")

    # --- Phase 5 agents (chat) + Phase 3 RAG (embeddings) — single OpenAI key ---
    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    openai_chat_model: str = Field(
        default="gpt-4o",
        validation_alias="OPENAI_CHAT_MODEL",
        description="Main agent model (planner, writer, editor, humanizer, fact-checker)",
    )
    openai_chat_model_mini: str = Field(
        default="gpt-4o-mini",
        validation_alias="OPENAI_CHAT_MODEL_MINI",
        description="Smaller / cheaper model (memory keeper, tonality judge, humanizer scorer)",
    )
    openai_embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="OPENAI_EMBEDDING_MODEL",
    )
    openai_base_url: str | None = Field(
        default=None,
        validation_alias="OPENAI_BASE_URL",
        description="Optional API base URL (e.g. https://api.openai.com/v1 or a compatible proxy).",
    )
    openai_http_connect_timeout_seconds: float = Field(
        default=60.0,
        ge=5.0,
        le=300.0,
        validation_alias="OPENAI_HTTP_CONNECT_TIMEOUT_SECONDS",
        description="TCP connect timeout for OpenAI HTTP calls (slow networks / VPN).",
    )
    openai_http_read_timeout_seconds: float = Field(
        default=600.0,
        ge=30.0,
        le=3600.0,
        validation_alias="OPENAI_HTTP_READ_TIMEOUT_SECONDS",
        description="Read timeout per chat/embeddings request (planner/writer can be slow).",
    )
    pinecone_api_key: str | None = Field(default=None, validation_alias="PINECONE_API_KEY")
    pinecone_index_name: str = Field(default="aiuthor", validation_alias="PINECONE_INDEX_NAME")
    pinecone_rerank_model: str = Field(
        default="cohere-rerank-3.5",
        validation_alias="PINECONE_RERANK_MODEL",
        description="Pinecone Inference rerank model (hosted; uses PINECONE_API_KEY only).",
    )
    tavily_api_key: str | None = Field(default=None, validation_alias="TAVILY_API_KEY")
    wikipedia_lang: str = Field(
        default="en",
        min_length=2,
        max_length=8,
        validation_alias="WIKIPEDIA_LANG",
        description="Wikipedia edition for RAG (e.g. en, de). Public API — no Wikipedia API key.",
    )
    rag_dense_top_k: int = Field(default=20, ge=5, le=100, validation_alias="RAG_DENSE_TOP_K")
    rag_bm25_top_k: int = Field(default=20, ge=5, le=100, validation_alias="RAG_BM25_TOP_K")
    rag_rrf_k: int = Field(default=60, ge=1, validation_alias="RAG_RRF_K")
    rag_final_top_n: int = Field(default=5, ge=1, le=20, validation_alias="RAG_FINAL_TOP_N")

    # Token cost estimates (USD per million tokens) for ledger — tune to current OpenAI list pricing
    price_openai_primary_input_per_mtok: float = Field(
        default=2.5, validation_alias="PRICE_OPENAI_PRIMARY_INPUT_PER_MTOK"
    )
    price_openai_primary_output_per_mtok: float = Field(
        default=10.0, validation_alias="PRICE_OPENAI_PRIMARY_OUTPUT_PER_MTOK"
    )
    price_openai_mini_input_per_mtok: float = Field(
        default=0.15, validation_alias="PRICE_OPENAI_MINI_INPUT_PER_MTOK"
    )
    price_openai_mini_output_per_mtok: float = Field(
        default=0.6, validation_alias="PRICE_OPENAI_MINI_OUTPUT_PER_MTOK"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
