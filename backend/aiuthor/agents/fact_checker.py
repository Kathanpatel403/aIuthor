"""Fact-checker → softened chapter (OpenAI chat)."""

from __future__ import annotations

import json

from aiuthor.config.settings import Settings
from aiuthor.orchestrator.llm import completion_text, openai_client
from aiuthor.prompts.fact_checker_prompts import FACT_CHECKER_SYSTEM
from aiuthor.rag.schemas import ChapterFactPack


def run_fact_checker(text: str, fact_pack: ChapterFactPack, settings: Settings) -> str:
    if not settings.openai_api_key:
        return text
    facts = [{"text": c.text, "url": c.source_url, "title": c.source_title} for c in fact_pack.chunks]
    client = openai_client(settings)
    user = json.dumps({"facts": facts, "chapter": text}, indent=2)[:120000]
    return completion_text(
        client,
        model=settings.openai_chat_model,
        system=FACT_CHECKER_SYSTEM,
        user=user,
        max_tokens=12000,
        temperature=0.2,
        agent="fact_checker",
        settings=settings,
    )
