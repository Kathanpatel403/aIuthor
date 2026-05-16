"""OpenAI text embeddings (text-embedding-3-small)."""

from __future__ import annotations

from typing import Sequence

from aiuthor.config.settings import Settings, get_settings
from aiuthor.orchestrator.llm import openai_client


def embed_texts(
    texts: Sequence[str],
    *,
    settings: Settings | None = None,
    batch_size: int = 64,
) -> list[list[float]]:
    s = settings or get_settings()
    if not s.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is required for embeddings")
    client = openai_client(s)
    out: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = list(texts[i : i + batch_size])
        resp = client.embeddings.create(model=s.openai_embedding_model, input=batch)
        # API returns in input order
        ordered = sorted(resp.data, key=lambda d: d.index)
        out.extend([d.embedding for d in ordered])
    return out


def embed_query(query: str, *, settings: Settings | None = None) -> list[float]:
    return embed_texts([query], settings=settings)[0]
