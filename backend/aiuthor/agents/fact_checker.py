"""Fact-checker → softened chapter (Sonnet)."""

from __future__ import annotations

import json

from aiuthor.config.settings import Settings
from aiuthor.orchestrator.llm import SONNET_MODEL, anthropic_client, completion_text
from aiuthor.prompts.fact_checker_prompts import FACT_CHECKER_SYSTEM
from aiuthor.rag.schemas import ChapterFactPack


def run_fact_checker(text: str, fact_pack: ChapterFactPack, settings: Settings) -> str:
    if not settings.anthropic_api_key:
        return text
    facts = [{"text": c.text, "url": c.source_url, "title": c.source_title} for c in fact_pack.chunks]
    client = anthropic_client(settings)
    user = json.dumps({"facts": facts, "chapter": text}, indent=2)[:120000]
    return completion_text(
        client,
        model=SONNET_MODEL,
        system=FACT_CHECKER_SYSTEM,
        user=user,
        max_tokens=12000,
        temperature=0.2,
        agent="fact_checker",
        settings=settings,
    )
