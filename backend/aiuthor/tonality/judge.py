"""LLM-as-judge: tonality fidelity 0–1 (OpenAI mini)."""

from __future__ import annotations

import json
import re

from aiuthor.config.settings import Settings, get_settings
from aiuthor.orchestrator.llm import completion_text, openai_client


def score_tonality_fidelity(
    text: str,
    target_tonality: str,
    *,
    settings: Settings | None = None,
) -> float:
    """
    Returns a score in [0, 1]. On parse failure or missing API key, returns neutral 0.5.
    """
    s = settings or get_settings()
    if not s.openai_api_key or len(text.strip()) < 40:
        return 0.5
    client = openai_client(s)
    prompt = (
        "You evaluate whether prose matches a target tonality.\n"
        f"Target tonality id: {target_tonality}\n"
        "Return ONLY JSON: {\"score\": <float 0..1>, \"rationale\": <one sentence>}\n"
        "Criteria: vocabulary, rhythm, stance, hooks vs target; ignore factual correctness.\n"
        f"TEXT:\n{text[:6000]}\n"
    )
    raw = completion_text(
        client,
        model=s.openai_chat_model_mini,
        system="You output valid JSON only.",
        user=prompt,
        max_tokens=256,
        temperature=0.0,
        agent="tonality_judge",
        settings=s,
    )
    m = re.search(r"\{[\s\S]*\}", raw)
    if not m:
        return 0.5
    try:
        data = json.loads(m.group(0))
        sc = float(data.get("score", 0.5))
        return max(0.0, min(1.0, sc))
    except (json.JSONDecodeError, TypeError, ValueError):
        return 0.5
