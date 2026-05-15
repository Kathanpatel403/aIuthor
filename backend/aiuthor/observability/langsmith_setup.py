"""Apply LangSmith-related environment variables for downstream LangChain / LangGraph usage."""

from __future__ import annotations

import logging
import os

from aiuthor.config.settings import get_settings

logger = logging.getLogger(__name__)


def configure_langsmith_runtime_env() -> None:
    """
    Mirror pydantic settings into os.environ so LangChain SDKs pick up tracing
    without requiring users to export variables twice.
    """
    s = get_settings()
    if s.langchain_api_key:
        os.environ["LANGCHAIN_API_KEY"] = s.langchain_api_key
        os.environ["LANGCHAIN_TRACING_V2"] = "true" if s.langchain_tracing_v2 else "false"
        os.environ["LANGCHAIN_PROJECT"] = s.langchain_project
        logger.info("LangSmith tracing configured for project=%s", s.langchain_project)
    else:
        os.environ.pop("LANGCHAIN_API_KEY", None)
        if s.langchain_tracing_v2:
            logger.warning(
                "LANGCHAIN_TRACING_V2 is true but LANGCHAIN_API_KEY is unset; "
                "LangSmith runs will be no-ops until a key is provided."
            )
