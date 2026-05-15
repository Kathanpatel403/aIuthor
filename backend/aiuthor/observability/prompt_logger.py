"""Append structured prompt logs for each LLM call."""

from __future__ import annotations

from aiuthor.observability.context import get_collector, utc_iso


def log_prompt(
    *,
    agent: str,
    model: str,
    system: str,
    user: str,
    response_text: str,
    temperature: float,
    max_tokens: int,
) -> None:
    coll = get_collector()
    if coll is None:
        return
    coll.prompts.append(
        {
            "ts": utc_iso(),
            "agent": agent,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "system": system[:24000],
            "user": user[:24000],
            "response_preview": response_text[:4000],
            "response_chars": len(response_text),
        }
    )
