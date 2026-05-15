"""Cohere rerank-english-v3.0 (optional)."""

from __future__ import annotations

import cohere

from aiuthor.config.settings import Settings, get_settings


def rerank_documents(
    query: str,
    documents: list[str],
    *,
    top_n: int,
    settings: Settings | None = None,
) -> list[tuple[int, float]]:
    """
    Returns (original_index, relevance_score) sorted by descending relevance.
    If COHERE_API_KEY is unset, returns identity order 0..len-1 with score 1.0.
    """
    s = settings or get_settings()
    if not s.cohere_api_key or not documents:
        return [(i, 1.0) for i in range(min(top_n, len(documents)))]
    try:
        client = cohere.Client(api_key=s.cohere_api_key)
        resp = client.rerank(
            model=s.cohere_rerank_model,
            query=query,
            documents=list(documents),
            top_n=min(top_n, len(documents)),
        )
        return [(r.index, float(r.relevance_score)) for r in resp.results]
    except Exception:
        return [(i, 1.0) for i in range(min(top_n, len(documents)))]
