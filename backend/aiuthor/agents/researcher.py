"""Researcher → `ChapterFactPack` via RAG."""

from __future__ import annotations

from aiuthor.config.settings import Settings
from aiuthor.rag.retriever import build_chapter_fact_pack
from aiuthor.rag.schemas import ChapterFactPack, ChapterResearchRequest
from aiuthor.schemas.brief import ChapterOutline


def run_researcher(
    book_id: str,
    chapter: ChapterOutline,
    settings: Settings,
    *,
    max_wiki: int = 2,
    max_tavily: int = 5,
) -> ChapterFactPack:
    topic = f"{chapter.title}. {chapter.summary}"
    req = ChapterResearchRequest(
        book_id=book_id,
        chapter_topic=topic,
        max_wiki_articles=max_wiki,
        max_tavily_results=max_tavily,
        ingest_namespace=f"ch{chapter.number}",
    )
    return build_chapter_fact_pack(req, settings=settings)
