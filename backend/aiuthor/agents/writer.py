"""Writer → raw Markdown chapter (Sonnet + tonality cascade)."""

from __future__ import annotations

import json

from aiuthor.config.settings import Settings
from aiuthor.orchestrator.llm import SONNET_MODEL, anthropic_client, completion_text
from aiuthor.prompts.writer_prompts import WRITER_SYSTEM_PREFIX
from aiuthor.rag.schemas import ChapterFactPack
from aiuthor.schemas.brief import ChapterOutline
from aiuthor.tonality.cascader import cascade_system_modifier


def run_writer(
    outline_title: str,
    genre: str,
    chapter: ChapterOutline,
    fact_pack: ChapterFactPack,
    tonality: str,
    target_words: int,
    settings: Settings,
) -> str:
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY required for writer")
    tone = cascade_system_modifier("chapter_body", tonality)
    system = WRITER_SYSTEM_PREFIX + "\n" + tone
    sources = [
        {"title": c.source_title, "url": c.source_url, "text": c.text}
        for c in fact_pack.chunks[:12]
    ]
    user = json.dumps(
        {
            "book_title": outline_title,
            "genre": genre,
            "chapter": chapter.model_dump(),
            "target_words": target_words,
            "source_passages": sources,
        },
        indent=2,
    )
    client = anthropic_client(settings)
    return completion_text(
        client,
        model=SONNET_MODEL,
        system=system,
        user=user,
        max_tokens=12000,
        temperature=0.65,
    )
