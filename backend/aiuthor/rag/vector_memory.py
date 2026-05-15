"""In-process dense vector index (dev / no Pinecone)."""

from __future__ import annotations

import math
import threading
from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

from aiuthor.rag.schemas import TextChunk


def _normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    if n < 1e-12:
        return v
    return v / n


@dataclass
class _Stored:
    chunk_id: str
    vector: np.ndarray
    chunk: TextChunk


class MemoryVectorIndex:
    """Cosine top-k over all vectors in a namespace (book-scoped)."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._by_ns: dict[str, list[_Stored]] = {}

    def clear_namespace(self, namespace: str) -> None:
        with self._lock:
            self._by_ns[namespace] = []

    def upsert_chunks(
        self,
        namespace: str,
        chunks: Sequence[TextChunk],
        vectors: Sequence[list[float]],
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("chunks and vectors length mismatch")
        with self._lock:
            lane = self._by_ns.setdefault(namespace, [])
            for ch, vec in zip(chunks, vectors, strict=True):
                lane.append(
                    _Stored(
                        chunk_id=ch.chunk_id,
                        vector=np.array(vec, dtype=np.float32),
                        chunk=ch,
                    )
                )

    def query(self, namespace: str, query_vector: list[float], top_k: int) -> list[tuple[str, float, TextChunk]]:
        q = _normalize(np.array(query_vector, dtype=np.float32))
        with self._lock:
            lane = list(self._by_ns.get(namespace, []))
        if not lane:
            return []
        mat = np.stack([s.vector for s in lane])
        mat_n = mat / np.clip(np.linalg.norm(mat, axis=1, keepdims=True), 1e-12, None)
        sims = mat_n @ q
        order = np.argsort(-sims)[:top_k]
        out: list[tuple[str, float, TextChunk]] = []
        for i in order:
            s = lane[int(i)]
            out.append((s.chunk_id, float(sims[int(i)]), s.chunk))
        return out


_indexes: dict[int, MemoryVectorIndex] = {}
_idx_lock = threading.Lock()


def get_memory_vector_index() -> MemoryVectorIndex:
    """Process-wide singleton (same pattern as memory store)."""
    with _idx_lock:
        # single global index table with namespaces per book
        if 0 not in _indexes:
            _indexes[0] = MemoryVectorIndex()
        return _indexes[0]


def reset_memory_vector_index_for_tests() -> None:
    with _idx_lock:
        _indexes.clear()
