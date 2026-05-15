"""Chunk, embed, and upsert into dense store + corpus registry."""

from __future__ import annotations

from aiuthor.config.settings import Settings, get_settings
from aiuthor.rag.chunking import chunk_document
from aiuthor.rag.corpus_session import clear_namespace, replace_corpus
from aiuthor.rag.embeddings import embed_texts
from aiuthor.rag.pinecone_store import pinecone_delete_namespace, pinecone_upsert_chunks
from aiuthor.rag.schemas import RawDocument, TextChunk
from aiuthor.rag.vector_memory import get_memory_vector_index


def ingest_raw_documents(
    namespace: str,
    documents: list[RawDocument],
    *,
    settings: Settings | None = None,
    replace: bool = True,
) -> tuple[int, list[TextChunk]]:
    """
    Returns (num_chunks_ingested, chunks).

    When replace=True, clears prior corpus + memory vectors for namespace; Pinecone namespace
    is best-effort deleted when API key is configured.
    """
    s = settings or get_settings()
    all_chunks: list[TextChunk] = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    if not all_chunks:
        return 0, []

    if replace:
        clear_namespace(namespace)
        get_memory_vector_index().clear_namespace(namespace)
        if s.pinecone_api_key:
            try:
                pinecone_delete_namespace(namespace, settings=s)
            except Exception:
                # Namespace may not exist yet
                pass

    vectors = embed_texts([c.text for c in all_chunks], settings=s)
    replace_corpus(namespace, all_chunks)
    get_memory_vector_index().upsert_chunks(namespace, all_chunks, vectors)
    if s.pinecone_api_key:
        pinecone_upsert_chunks(namespace, all_chunks, vectors, settings=s)

    return len(all_chunks), all_chunks
