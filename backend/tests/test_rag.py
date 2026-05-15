"""RAG unit tests (no live OpenAI / Pinecone / Cohere by default)."""

from __future__ import annotations

import pytest

from aiuthor.config.settings import get_settings
from aiuthor.rag.bm25_index import ChunkBM25Index
from aiuthor.rag.chunking import chunk_text
from aiuthor.rag.corpus_session import reset_corpus_registry_for_tests
from aiuthor.rag.hybrid import reciprocal_rank_fusion
from aiuthor.rag.ingestion import ingest_raw_documents
from aiuthor.rag.retriever import retrieve_hybrid
from aiuthor.rag.schemas import RawDocument
from aiuthor.rag.vector_memory import reset_memory_vector_index_for_tests


@pytest.fixture(autouse=True)
def _clean_rag():
    reset_corpus_registry_for_tests()
    reset_memory_vector_index_for_tests()
    get_settings.cache_clear()
    yield
    reset_corpus_registry_for_tests()
    reset_memory_vector_index_for_tests()
    get_settings.cache_clear()


def test_chunking_respects_overlap():
    text = "word " * 800
    chunks = chunk_text(
        text,
        source_id="s1",
        title="t",
        source_url=None,
        source_type="web",
        target_tokens=50,
        overlap_tokens=10,
    )
    assert len(chunks) >= 2
    assert all(len(c.text) > 0 for c in chunks)


def test_rrf_merges_two_lists():
    fused = reciprocal_rank_fusion(
        [["a", "b", "c"], ["b", "d", "a"]],
        k=60,
    )
    ids = [x[0] for x in fused]
    assert "b" in ids[:2]


def test_bm25_orders_keyword_match():
    ids = ["c1", "c2", "c3"]
    docs = [
        "cats sleep all day on the sofa",
        "dogs run in the park every morning",
        "the park has morning yoga for dogs",
    ]
    ix = ChunkBM25Index(ids, docs)
    top = ix.top_k("dogs park morning", 2)
    assert top[0][0] in ("c2", "c3")


def test_ingest_and_retrieve_hybrid(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-placeholder")
    get_settings.cache_clear()
    settings = get_settings()

    def fake_embed_texts(texts, **kwargs: object):
        return [[float((i + j) % 17) / 17.0 for j in range(1536)] for i in range(len(texts))]

    def fake_embed_query(query: str, **kwargs: object):
        return fake_embed_texts([query], **kwargs)[0]

    monkeypatch.setattr("aiuthor.rag.embeddings.embed_texts", fake_embed_texts)
    monkeypatch.setattr("aiuthor.rag.embeddings.embed_query", fake_embed_query)

    docs = [
        RawDocument(
            source_id="u1",
            title="Emergency fund",
            text="An emergency fund is cash reserved for unexpected expenses. "
            "Start with one month of expenses then grow to three to six months.",
            source_url="https://example.test/emergency-fund",
            source_type="web",
        ),
        RawDocument(
            source_id="u2",
            title="Budgeting",
            text="Budgeting means tracking income and spending each month. "
            "The fifty thirty twenty rule splits needs wants and savings.",
            source_url="https://example.test/budget",
            source_type="web",
        ),
    ]
    n, _ = ingest_raw_documents("booktest:default", docs, settings=settings, replace=True)
    assert n >= 2

    pack = retrieve_hybrid("booktest:default", "emergency fund basics", settings=settings)
    assert len(pack.chunks) >= 1
    assert "emergency" in pack.chunks[0].text.lower() or "fund" in pack.chunks[0].text.lower()
