"""Humanizer → tightened prose (OpenAI chat)."""

from __future__ import annotations

from aiuthor.config.settings import Settings
from aiuthor.humanizer.scorer import banned_phrase_catalog_for_prompts
from aiuthor.orchestrator.llm import completion_text, openai_client
from aiuthor.prompts.humanizer_prompts import HUMANIZER_SYSTEM
from aiuthor.tonality.cascader import cascade_system_modifier


def run_humanizer(draft: str, tonality: str, settings: Settings) -> str:
    if not settings.openai_api_key:
        return draft
    tone = cascade_system_modifier("chapter_body", tonality)
    system = (
        HUMANIZER_SYSTEM
        + "\n## Banned phrase catalog (do not use verbatim; remove if present)\n"
        + banned_phrase_catalog_for_prompts()
        + "\n"
        + tone
    )
    client = openai_client(settings)
    return completion_text(
        client,
        model=settings.openai_chat_model,
        system=system,
        user=draft,
        max_tokens=12000,
        temperature=0.5,
        agent="humanizer",
        settings=settings,
    )
