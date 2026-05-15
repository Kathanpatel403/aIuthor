"""Token-aligned chunking (~500 tokens, ~50 overlap) via tiktoken."""

from __future__ import annotations

import uuid

import tiktoken

from aiuthor.rag.schemas import RawDocument, TextChunk

DEFAULT_ENCODING = "cl100k_base"
TARGET_TOKENS = 500
OVERLAP_TOKENS = 50


def get_encoder():
    return tiktoken.get_encoding(DEFAULT_ENCODING)


def chunk_text(
    text: str,
    *,
    source_id: str,
    title: str,
    source_url: str | None,
    source_type: str,
    target_tokens: int = TARGET_TOKENS,
    overlap_tokens: int = OVERLAP_TOKENS,
) -> list[TextChunk]:
    enc = get_encoder()
    tokens = enc.encode(text.strip())
    if not tokens:
        return []

    chunks: list[TextChunk] = []
    step = max(1, target_tokens - overlap_tokens)
    i = 0
    while i < len(tokens):
        window = tokens[i : i + target_tokens]
        piece = enc.decode(window)
        start = i
        end = min(i + target_tokens, len(tokens))
        chunks.append(
            TextChunk(
                chunk_id=f"{source_id}::chunk-{uuid.uuid4().hex[:12]}",
                text=piece.strip(),
                source_id=source_id,
                title=title,
                source_url=source_url,
                source_type=source_type,
                token_start=start,
                token_end=end,
            )
        )
        i += step
        if end >= len(tokens):
            break
    return [c for c in chunks if c.text]


def chunk_document(doc: RawDocument, **kwargs: object) -> list[TextChunk]:
    st = doc.source_type
    return chunk_text(
        doc.text,
        source_id=doc.source_id,
        title=doc.title,
        source_url=doc.source_url,
        source_type=st,
        target_tokens=int(kwargs.get("target_tokens", TARGET_TOKENS)),
        overlap_tokens=int(kwargs.get("overlap_tokens", OVERLAP_TOKENS)),
    )
