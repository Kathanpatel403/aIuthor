"""Thread-safe registry of chunk text/metadata per RAG namespace (BM25 + rerank)."""

from __future__ import annotations

import copy
import threading

from aiuthor.rag.schemas import TextChunk

_lock = threading.RLock()
_chunks_by_ns: dict[str, list[TextChunk]] = {}
_chunk_map_by_ns: dict[str, dict[str, TextChunk]] = {}


def replace_corpus(namespace: str, chunks: list[TextChunk]) -> None:
    with _lock:
        _chunks_by_ns[namespace] = copy.deepcopy(chunks)
        _chunk_map_by_ns[namespace] = {c.chunk_id: copy.deepcopy(c) for c in chunks}


def append_corpus(namespace: str, chunks: list[TextChunk]) -> None:
    with _lock:
        cur = _chunks_by_ns.setdefault(namespace, [])
        cmap = _chunk_map_by_ns.setdefault(namespace, {})
        for c in chunks:
            cc = copy.deepcopy(c)
            cur.append(cc)
            cmap[cc.chunk_id] = cc


def list_chunks(namespace: str) -> list[TextChunk]:
    with _lock:
        return list(_chunks_by_ns.get(namespace, []))


def chunk_map(namespace: str) -> dict[str, TextChunk]:
    with _lock:
        return dict(_chunk_map_by_ns.get(namespace, {}))


def clear_namespace(namespace: str) -> None:
    with _lock:
        _chunks_by_ns.pop(namespace, None)
        _chunk_map_by_ns.pop(namespace, None)


def reset_corpus_registry_for_tests() -> None:
    with _lock:
        _chunks_by_ns.clear()
        _chunk_map_by_ns.clear()
