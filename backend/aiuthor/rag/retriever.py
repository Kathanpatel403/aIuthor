"""Hybrid dense + BM25 + Cohere rerank → `ChapterFactPack` (Researcher input)."""

from __future__ import annotations

from aiuthor.config.settings import Settings, get_settings
from aiuthor.rag.bm25_index import ChunkBM25Index
from aiuthor.rag.corpus_session import chunk_map, list_chunks
from aiuthor.rag.embeddings import embed_query
from aiuthor.rag.hybrid import reciprocal_rank_fusion
from aiuthor.rag.ingestion import ingest_raw_documents
from aiuthor.rag.pinecone_store import pinecone_query
from aiuthor.rag.reranker import rerank_documents
from aiuthor.rag.schemas import ChapterFactPack, ChapterResearchRequest, GroundedChunk, RawDocument
from aiuthor.rag.sources.web_search import fetch_tavily_documents
from aiuthor.rag.sources.wikipedia import fetch_wikipedia_documents
from aiuthor.rag.vector_memory import get_memory_vector_index


def rag_namespace(book_id: str, slot: str | None) -> str:
    safe = (slot or "default").strip() or "default"
    return f"{book_id.strip()}:{safe}"


def gather_raw_documents(req: ChapterResearchRequest, settings: Settings) -> tuple[list[RawDocument], list[str]]:
    warnings: list[str] = []
    docs: list[RawDocument] = []
    if req.max_wiki_articles > 0:
        try:
            docs.extend(
                fetch_wikipedia_documents(
                    req.chapter_topic,
                    lang=req.wikipedia_lang,
                    max_articles=req.max_wiki_articles,
                )
            )
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"wikipedia_failed:{exc.__class__.__name__}")
    if req.max_tavily_results > 0:
        if settings.tavily_api_key:
            try:
                docs.extend(
                    fetch_tavily_documents(
                        req.chapter_topic,
                        api_key=settings.tavily_api_key,
                        max_results=req.max_tavily_results,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                warnings.append(f"tavily_failed:{exc.__class__.__name__}")
        else:
            warnings.append("tavily_skipped_no_api_key")
    return docs, warnings


def retrieve_hybrid(
    namespace: str,
    query: str,
    *,
    settings: Settings,
) -> ChapterFactPack:
    """Assume corpus already ingested into namespace."""
    warnings: list[str] = []
    book_id = namespace.split(":", 1)[0] if ":" in namespace else namespace

    if not settings.openai_api_key:
        return ChapterFactPack(
            book_id=book_id,
            chapter_topic=query,
            chunks=[],
            warnings=["openai_missing_cannot_embed"],
        )

    chunks = list_chunks(namespace)
    if not chunks:
        return ChapterFactPack(
            book_id=book_id,
            chapter_topic=query,
            chunks=[],
            warnings=["empty_corpus_run_ingest_first"],
        )

    qv = embed_query(query, settings=settings)
    dense_k = settings.rag_dense_top_k
    bm25_k = settings.rag_bm25_top_k

    if settings.pinecone_api_key:
        try:
            dense_hits = pinecone_query(namespace, qv, dense_k, settings=settings)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"pinecone_query_failed:{exc.__class__.__name__}")
            dense_hits = get_memory_vector_index().query(namespace, qv, dense_k)
    else:
        dense_hits = get_memory_vector_index().query(namespace, qv, dense_k)

    dense_ranked = [cid for cid, _, _ in dense_hits]
    dense_score = {cid: score for cid, score, _ in dense_hits}

    bm25 = ChunkBM25Index([c.chunk_id for c in chunks], [c.text for c in chunks])
    bm25_hits = bm25.top_k(query, bm25_k)
    bm25_ranked = [cid for cid, _ in bm25_hits]
    bm25_score = dict(bm25_hits)

    fused = reciprocal_rank_fusion([dense_ranked, bm25_ranked], k=settings.rag_rrf_k)
    rrf_by_id = dict(fused)

    pool_n = max(settings.rag_final_top_n * 5, 24)
    pool_ids = [cid for cid, _ in fused[:pool_n]]
    cmap = chunk_map(namespace)
    pool_rows = [(cid, cmap[cid].text) for cid in pool_ids if cid in cmap]
    pool_ids = [a for a, _ in pool_rows]
    pool_docs = [b for _, b in pool_rows]

    rerank_pairs = rerank_documents(
        query,
        pool_docs,
        top_n=min(len(pool_docs), max(settings.rag_final_top_n * 4, 12)),
        settings=settings,
    )
    if not settings.cohere_api_key:
        warnings.append("cohere_skipped_rerank_using_order")

    ordered_chunk_ids: list[str] = []
    rerank_by_id: dict[str, float] = {}
    for idx, score in rerank_pairs:
        if 0 <= idx < len(pool_ids):
            cid = pool_ids[idx]
            ordered_chunk_ids.append(cid)
            rerank_by_id[cid] = score

    final_ids = ordered_chunk_ids[: settings.rag_final_top_n]

    out_chunks: list[GroundedChunk] = []
    for cid in final_ids:
        ch = cmap.get(cid)
        if not ch:
            continue
        out_chunks.append(
            GroundedChunk(
                chunk_id=ch.chunk_id,
                text=ch.text,
                source_title=ch.title,
                source_url=ch.source_url,
                source_type=ch.source_type,
                score_dense=dense_score.get(cid),
                score_bm25=bm25_score.get(cid),
                score_rrf=rrf_by_id.get(cid),
                score_rerank=rerank_by_id.get(cid),
            )
        )

    return ChapterFactPack(book_id=book_id, chapter_topic=query, chunks=out_chunks, warnings=warnings)


def build_chapter_fact_pack(
    req: ChapterResearchRequest,
    *,
    settings: Settings | None = None,
) -> ChapterFactPack:
    """
    End-to-end: fetch Wikipedia + Tavily → chunk → embed → upsert → hybrid retrieve → rerank.
    """
    s = settings or get_settings()
    ns = rag_namespace(req.book_id, req.ingest_namespace)
    docs, gather_warnings = gather_raw_documents(req, s)

    warnings = list(gather_warnings)
    if not docs:
        warnings.append("no_documents_from_sources")
        return ChapterFactPack(
            book_id=req.book_id,
            chapter_topic=req.chapter_topic,
            chunks=[],
            warnings=warnings,
        )

    if not s.openai_api_key:
        warnings.append("openai_missing_cannot_embed")
        return ChapterFactPack(
            book_id=req.book_id,
            chapter_topic=req.chapter_topic,
            chunks=[],
            warnings=warnings,
        )

    try:
        n_ingested, _ = ingest_raw_documents(ns, docs, settings=s, replace=True)
        if n_ingested == 0:
            warnings.append("ingestion_produced_zero_chunks")
    except Exception as exc:  # noqa: BLE001
        warnings.append(f"ingest_failed:{exc.__class__.__name__}")
        return ChapterFactPack(
            book_id=req.book_id,
            chapter_topic=req.chapter_topic,
            chunks=[],
            warnings=warnings,
        )

    pack = retrieve_hybrid(ns, req.chapter_topic, settings=s)
    pack.warnings = list({*warnings, *pack.warnings})
    return pack
