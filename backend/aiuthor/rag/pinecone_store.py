"""Pinecone dense lane (optional — requires PINECONE_API_KEY + index dim 1536)."""

from __future__ import annotations

from typing import Sequence

from pinecone import Pinecone

from aiuthor.config.settings import Settings
from aiuthor.rag.schemas import TextChunk

_META_TEXT_MAX = 32000


def _pinecone_client(settings: Settings) -> Pinecone:
    if not settings.pinecone_api_key:
        raise RuntimeError("PINECONE_API_KEY missing")
    return Pinecone(api_key=settings.pinecone_api_key)


def pinecone_upsert_chunks(
    namespace: str,
    chunks: Sequence[TextChunk],
    vectors: Sequence[list[float]],
    *,
    settings: Settings,
) -> None:
    index = _pinecone_client(settings).Index(settings.pinecone_index_name)
    batch: list[dict] = []
    for ch, vec in zip(chunks, vectors, strict=True):
        meta = {
            "text": ch.text[:_META_TEXT_MAX],
            "title": str(ch.title)[:1024],
            "source_id": str(ch.source_id)[:1024],
            "source_type": str(ch.source_type)[:64],
        }
        if ch.source_url:
            meta["source_url"] = str(ch.source_url)[:2048]
        batch.append({"id": ch.chunk_id, "values": list(vec), "metadata": meta})
    # Pinecone upsert in batches of 100
    for i in range(0, len(batch), 100):
        index.upsert(vectors=batch[i : i + 100], namespace=namespace)


def pinecone_query(
    namespace: str,
    query_vector: list[float],
    top_k: int,
    *,
    settings: Settings,
) -> list[tuple[str, float, TextChunk]]:
    index = _pinecone_client(settings).Index(settings.pinecone_index_name)
    res = index.query(
        vector=list(query_vector),
        top_k=top_k,
        namespace=namespace,
        include_metadata=True,
    )
    out: list[tuple[str, float, TextChunk]] = []
    for m in res.matches or []:
        md = m.metadata or {}
        text = str(md.get("text", ""))
        title = str(md.get("title", ""))
        sid = str(md.get("source_id", m.id))
        st = str(md.get("source_type", "web"))
        url = md.get("source_url")
        surl = str(url).strip() if url else None
        if surl in ("", "None", "none"):
            surl = None
        ch = TextChunk(
            chunk_id=m.id,
            text=text,
            source_id=sid,
            title=title,
            source_url=surl,
            source_type=st,
        )
        score = float(m.score) if m.score is not None else 0.0
        out.append((m.id, score, ch))
    return out


def pinecone_delete_namespace(namespace: str, *, settings: Settings) -> None:
    index = _pinecone_client(settings).Index(settings.pinecone_index_name)
    index.delete(delete_all=True, namespace=namespace)
