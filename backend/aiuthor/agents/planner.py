"""Planner → `BookOutline` JSON (Sonnet)."""

from __future__ import annotations

import json
import re

from aiuthor.config.settings import Settings
from aiuthor.orchestrator.llm import SONNET_MODEL, anthropic_client, completion_text
from aiuthor.orchestrator.router import with_retries
from aiuthor.prompts.planner_prompts import PLANNER_SYSTEM
from aiuthor.schemas.brief import BookOutline, UserBrief


def run_planner(brief: UserBrief, settings: Settings) -> BookOutline:
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY required for planner")

    def _once() -> BookOutline:
        client = anthropic_client(settings)
        user = json.dumps(brief.model_dump(), indent=2)
        raw = completion_text(
            client,
            model=SONNET_MODEL,
            system=PLANNER_SYSTEM,
            user=user,
            max_tokens=4096,
            temperature=0.3,
            agent="planner",
            settings=settings,
        )
        m = re.search(r"\{[\s\S]*\}", raw)
        if not m:
            raise ValueError("planner returned no JSON object")
        return BookOutline.model_validate_json(m.group(0))

    return with_retries(_once, attempts=2, label="planner")
