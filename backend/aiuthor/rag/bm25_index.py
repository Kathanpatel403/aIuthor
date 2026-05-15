"""BM25Okapi over chunk texts (keyword lane for hybrid retrieval)."""

from __future__ import annotations

import re
from typing import Sequence

from rank_bm25 import BM25Okapi

_token_re = re.compile(r"[a-z0-9]+", re.I)


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _token_re.findall(text)]


class ChunkBM25Index:
    def __init__(self, chunk_ids: Sequence[str], documents: Sequence[str]) -> None:
        self.chunk_ids = list(chunk_ids)
        tokenized = [tokenize(d) for d in documents]
        if not any(tokenized):
            self._bm25: BM25Okapi | None = None
        else:
            self._bm25 = BM25Okapi(tokenized)

    def top_k(self, query: str, k: int) -> list[tuple[str, float]]:
        if not self.chunk_ids or self._bm25 is None:
            return []
        q = tokenize(query)
        if not q:
            return []
        scores = self._bm25.get_scores(q)
        ranked = sorted(zip(self.chunk_ids, scores), key=lambda x: -x[1])
        return ranked[:k]
