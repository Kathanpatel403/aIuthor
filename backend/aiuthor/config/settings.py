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


@lru_cache
def get_settings() -> Settings:
    return Settings()
