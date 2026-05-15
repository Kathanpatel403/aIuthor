"""Typed RAG payloads (Phase 3)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RawDocument(BaseModel):
    """One normalized source before chunking."""

    source_id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)
    source_url: str | None = None
    source_type: Literal["wikipedia", "web", "pdf", "user"] = "web"


class TextChunk(BaseModel):
    """Chunk with stable id for vector + BM25 lanes."""

    chunk_id: str
    text: str
    source_id: str
    title: str
    source_url: str | None = None
    source_type: str = "web"
    token_start: int = 0
    token_end: int = 0


class GroundedChunk(BaseModel):
    """Single retrieval unit after hybrid + optional rerank."""

    chunk_id: str
    text: str
    source_title: str
    source_url: str | None = None
    source_type: str = "web"
    score_dense: float | None = None
    score_bm25: float | None = None
    score_rrf: float | None = None
    score_rerank: float | None = None


class ChapterFactPack(BaseModel):
    """Researcher → Writer handoff: grounded passages for one chapter topic."""

    book_id: str
    chapter_topic: str
    chunks: list[GroundedChunk] = Field(default_factory=list)
    retrieved_at: datetime = Field(default_factory=utcnow)
    warnings: list[str] = Field(
        default_factory=list,
        description="e.g. missing API keys, empty corpus",
    )


class ChapterResearchRequest(BaseModel):
    book_id: str = Field(..., min_length=1)
    chapter_topic: str = Field(..., min_length=2)
    wikipedia_lang: str = Field(default="en", min_length=2, max_length=8)
    max_wiki_articles: int = Field(default=2, ge=0, le=5)
    max_tavily_results: int = Field(default=5, ge=0, le=10)
    ingest_namespace: str | None = Field(
        default=None,
        description="Optional suffix to isolate corpora within the same book_id",
    )
