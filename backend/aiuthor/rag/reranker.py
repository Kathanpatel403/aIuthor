"""Pinecone Inference rerank (e.g. cohere-rerank-3.5) — single vendor API key."""

from __future__ import annotations

import logging

from pinecone import Pinecone

from aiuthor.config.settings import Settings, get_settings

logger = logging.getLogger(__name__)


def rerank_documents(
    query: str,
    documents: list[str],
    *,
    top_n: int,
    settings: Settings | None = None,
) -> list[tuple[int, float]]:
    """
    Returns (original_index, relevance_score) sorted by descending relevance.
    Uses Pinecone's hosted rerank model (Cohere-backed options such as `cohere-rerank-3.5`).
    If PINECONE_API_KEY is unset, returns the first `top_n` indices in order with score 1.0.
    """
    s = settings or get_settings()
    if not s.pinecone_api_key or not documents:
        return [(i, 1.0) for i in range(min(top_n, len(documents)))]

    try:
        pc = Pinecone(api_key=s.pinecone_api_key)
        inf = getattr(pc, "inference", None)
        if inf is None or not hasattr(inf, "rerank"):
            logger.warning("Pinecone SDK has no inference.rerank; using RRF order only")
            return [(i, 1.0) for i in range(min(top_n, len(documents)))]
        docs_payload = [{"id": str(i), "text": (d or "")[:16000]} for i, d in enumerate(documents)]
        res = inf.rerank(
            model=s.pinecone_rerank_model,
            query=query,
            documents=docs_payload,
            top_n=min(top_n, len(documents)),
            parameters={"truncate": "END"},
        )
        ranked: list[tuple[int, float]] = []
        data = getattr(res, "data", None) or getattr(res, "results", None)
        if data is None and isinstance(res, dict):
            data = res.get("data")
        if not data:
            return [(i, 1.0) for i in range(min(top_n, len(documents)))]
        for item in data:
            idx: int | None = None
            score: float = 0.0
            if isinstance(item, dict):
                idx = item.get("index")
                if idx is None and item.get("id") is not None:
                    try:
                        idx = int(str(item["id"]))
                    except ValueError:
                        idx = None
                score = float(item.get("score", item.get("relevance_score", 0.0)))
            else:
                idx = getattr(item, "index", None)
                score = float(getattr(item, "score", 0.0) or 0.0)
            if idx is None:
                continue
            ranked.append((int(idx), score))
        if not ranked:
            return [(i, 1.0) for i in range(min(top_n, len(documents)))]
        ranked.sort(key=lambda x: -x[1])
        return ranked[: min(top_n, len(ranked))]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Pinecone rerank failed: %s", exc)
        return [(i, 1.0) for i in range(min(top_n, len(documents)))]
