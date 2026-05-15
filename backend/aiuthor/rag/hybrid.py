"""Reciprocal Rank Fusion for dense + BM25 list merge."""

from __future__ import annotations


def reciprocal_rank_fusion(
    ranked_lists: list[list[str]],
    *,
    k: int = 60,
) -> list[tuple[str, float]]:
    """
    Each inner list is chunk_ids ordered by descending relevance for that retriever.
    Returns chunk_id -> RRF score sorted high to low.
    """
    scores: dict[str, float] = {}
    for ids in ranked_lists:
        for rank, cid in enumerate(ids):
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank + 1)
    return sorted(scores.items(), key=lambda x: -x[1])
