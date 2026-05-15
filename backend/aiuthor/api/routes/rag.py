"""RAG API — chapter fact pack for Researcher agent (Phase 3)."""

from __future__ import annotations

from fastapi import APIRouter

from aiuthor.rag.retriever import build_chapter_fact_pack
from aiuthor.rag.schemas import ChapterFactPack, ChapterResearchRequest

router = APIRouter()


@router.post("/chapter-fact-pack", response_model=ChapterFactPack)
def chapter_fact_pack(body: ChapterResearchRequest) -> ChapterFactPack:
    """
    Fetch grounded sources (Wikipedia + Tavily), ingest into dense + BM25 lanes,
    then hybrid retrieve + Cohere rerank. Requires `OPENAI_API_KEY` for embeddings.
    """
    return build_chapter_fact_pack(body)
