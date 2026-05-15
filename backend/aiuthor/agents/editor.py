"""Editor → callbacks woven in (Sonnet)."""

from __future__ import annotations

from aiuthor.config.settings import Settings
from aiuthor.memory.callback_index import CallbackIndex
from aiuthor.orchestrator.llm import SONNET_MODEL, anthropic_client, completion_text
from aiuthor.prompts.editor_prompts import EDITOR_SYSTEM
from aiuthor.tonality.cascader import cascade_system_modifier


def run_editor(book_id: str, chapter_number: int, text: str, tonality: str, settings: Settings) -> str:
    if not settings.anthropic_api_key:
        return text
    ix = CallbackIndex(book_id)
    prior = [c.model_dump() for c in ix.list_all() if c.to_chapter <= chapter_number]
    tone = cascade_system_modifier("chapter_body", tonality)
    client = anthropic_client(settings)
    user = f"Current chapter number: {chapter_number}\nCallback index (JSON):\n{prior}\n\nCHAPTER:\n{text}"
    return completion_text(
        client,
        model=SONNET_MODEL,
        system=EDITOR_SYSTEM + "\n" + tone,
        user=user,
        max_tokens=12000,
        temperature=0.4,
    )
