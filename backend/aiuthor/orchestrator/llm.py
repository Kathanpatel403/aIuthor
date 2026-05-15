"""Anthropic clients + message helpers (Phase 5) + observability hooks (Phase 6)."""

from __future__ import annotations

import anthropic

from aiuthor.config.settings import Settings
from aiuthor.observability.prompt_logger import log_prompt
from aiuthor.observability.token_cost_ledger import record_llm_usage

SONNET_MODEL = "claude-sonnet-4-20250514"
HAIKU_MODEL = "claude-haiku-4-5-20251001"


def anthropic_client(settings: Settings) -> anthropic.Anthropic:
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def completion_text(
    client: anthropic.Anthropic,
    *,
    model: str,
    system: str,
    user: str,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    agent: str | None = None,
    settings: Settings | None = None,
) -> str:
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    parts: list[str] = []
    for block in msg.content:
        if block.type == "text":
            parts.append(block.text)
    text = "".join(parts).strip()

    usage = getattr(msg, "usage", None)
    inp = int(getattr(usage, "input_tokens", 0) or 0) if usage else 0
    out = int(getattr(usage, "output_tokens", 0) or 0) if usage else 0

    if agent:
        log_prompt(
            agent=agent,
            model=model,
            system=system,
            user=user,
            response_text=text,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        if inp + out > 0:
            from aiuthor.config.settings import get_settings as _gs

            record_llm_usage(
                agent=agent,
                model=model,
                input_tokens=inp,
                output_tokens=out,
                settings=settings or _gs(),
            )

    return text
