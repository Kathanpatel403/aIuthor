"""OpenAI chat clients + completion helpers + observability hooks (Phase 5–6)."""

from __future__ import annotations

import httpx
from openai import OpenAI

from aiuthor.config.settings import Settings
from aiuthor.observability.prompt_logger import log_prompt
from aiuthor.observability.token_cost_ledger import record_llm_usage

__all__ = ["openai_client", "completion_text"]


def openai_client(settings: Settings) -> OpenAI:
    """Shared OpenAI SDK client with explicit connect/read timeouts (avoids default short connect limit)."""
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    timeout = httpx.Timeout(
        connect=settings.openai_http_connect_timeout_seconds,
        read=settings.openai_http_read_timeout_seconds,
        write=120.0,
        pool=10.0,
    )
    kwargs: dict = {
        "api_key": settings.openai_api_key,
        "timeout": timeout,
        "max_retries": 2,
    }
    bu = (settings.openai_base_url or "").strip()
    if bu:
        kwargs["base_url"] = bu
    return OpenAI(**kwargs)


def completion_text(
    client: OpenAI,
    *,
    model: str,
    system: str,
    user: str,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    agent: str | None = None,
    settings: Settings | None = None,
) -> str:
    resp = client.chat.completions.create(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    choice = resp.choices[0].message
    text = (choice.content or "").strip()

    usage = getattr(resp, "usage", None)
    inp = int(getattr(usage, "prompt_tokens", 0) or 0) if usage else 0
    out = int(getattr(usage, "completion_tokens", 0) or 0) if usage else 0

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
