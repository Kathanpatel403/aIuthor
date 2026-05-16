"""Writer → raw Markdown chapter (OpenAI chat + tonality cascade + memory callbacks)."""

from __future__ import annotations

import json

from aiuthor.config.settings import Settings
from aiuthor.memory.callback_index import CallbackIndex
from aiuthor.memory.concept_bible import ConceptBible
from aiuthor.orchestrator.llm import completion_text, openai_client
from aiuthor.prompts.writer_prompts import WRITER_SYSTEM_PREFIX
from aiuthor.rag.schemas import ChapterFactPack
from aiuthor.schemas.brief import ChapterOutline
from aiuthor.tonality.cascader import cascade_system_modifier


def _build_callback_context(book_id: str, chapter_number: int) -> str:
    """Return a compact JSON string of prior callbacks and key concepts for the writer."""
    if chapter_number <= 1:
        return ""

    cb_idx = CallbackIndex(book_id)
    bible = ConceptBible(book_id)

    prior_callbacks = [
        {"from": c.from_chapter, "to": c.to_chapter, "snippet": c.snippet[:200], "kind": c.kind}
        for c in cb_idx.list_all()
        if c.from_chapter < chapter_number
    ][:10]  # cap at 10 to keep token budget reasonable

    prior_concepts = [
        {"term": c.term, "defined_in": c.first_mentioned_chapter, "definition": c.definition[:200]}
        for c in bible.list_all()
        if c.first_mentioned_chapter < chapter_number
    ][:15]

    if not prior_callbacks and not prior_concepts:
        return ""

    return json.dumps(
        {"prior_callbacks": prior_callbacks, "established_concepts": prior_concepts},
        indent=2,
    )


def run_writer(
    outline_title: str,
    genre: str,
    chapter: ChapterOutline,
    fact_pack: ChapterFactPack,
    tonality: str,
    target_words: int,
    settings: Settings,
    book_id: str = "",
) -> str:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY required for writer")

    tone = cascade_system_modifier("chapter_body", tonality)
    cb_context = _build_callback_context(book_id, chapter.number) if book_id else ""

    system = WRITER_SYSTEM_PREFIX
    if cb_context:
        system += f"\n\n## CALLBACK CONTEXT (from earlier chapters — reference at least one):\n{cb_context}\n"
    system += "\n" + tone

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
    client = openai_client(settings)
    return completion_text(
        client,
        model=settings.openai_chat_model,
        system=system,
        user=user,
        max_tokens=12000,
        temperature=0.65,
        agent="writer",
        settings=settings,
    )
