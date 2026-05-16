"""LLM-as-judge for AI-tell violations (OpenAI mini)."""

from __future__ import annotations

import json
import re

from aiuthor.config.settings import Settings, get_settings
from aiuthor.humanizer.rules import BANNED_PHRASES, list_violations
from aiuthor.orchestrator.llm import completion_text, openai_client


def ai_tell_violations_llm(text: str, *, settings: Settings | None = None) -> list[str]:
    """Combine deterministic scan + small judge pass."""
    base = list_violations(text)
    s = settings or get_settings()
    if not s.openai_api_key or len(text) < 200:
        return base
    client = openai_client(s)
    user = (
        "List AI-writing tells in the prose (filler, symmetric contrast, mechanical triads, "
        "over-signposting). Return JSON {\"tells\": [\"...\"] } only, max 12 items.\n\n"
        f"TEXT:\n{text[:8000]}\n"
    )
    raw = completion_text(
        client,
        model=s.openai_chat_model_mini,
        system="Return JSON only.",
        user=user,
        max_tokens=400,
        temperature=0.0,
        agent="ai_tell_judge",
        settings=s,
    )
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return base
    try:
        data = json.loads(m.group(0))
        tells = data.get("tells") or []
        for item in tells:
            if isinstance(item, str) and item.strip():
                base.append(f"llm_tell:{item.strip()[:200]}")
    except (json.JSONDecodeError, TypeError):
        pass
    # de-dupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for x in base:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def banned_phrase_catalog_for_prompts() -> str:
    return "\n".join(f"- {p}" for p in BANNED_PHRASES)
