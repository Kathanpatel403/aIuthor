"""Anthropic usage → USD estimates (configurable via Settings)."""

from __future__ import annotations

from typing import Any

from aiuthor.config.settings import Settings, get_settings
from aiuthor.observability.context import get_collector, get_current_agent, utc_iso
from aiuthor.orchestrator.llm import HAIKU_MODEL, SONNET_MODEL


def _estimate_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    settings: Settings,
) -> float:
    """Rough list pricing; override via env if Anthropic changes rates."""
    # Defaults USD per million tokens (approximate placeholders — tune in production).
    if SONNET_MODEL in model or "sonnet-4" in model.lower():
        inp = settings.price_sonnet_input_per_mtok
        out = settings.price_sonnet_output_per_mtok
    elif HAIKU_MODEL in model or "haiku" in model.lower():
        inp = settings.price_haiku_input_per_mtok
        out = settings.price_haiku_output_per_mtok
    else:
        inp = settings.price_sonnet_input_per_mtok
        out = settings.price_sonnet_output_per_mtok
    return (input_tokens / 1_000_000.0) * inp + (output_tokens / 1_000_000.0) * out


def record_llm_usage(
    *,
    agent: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    settings: Settings | None = None,
) -> None:
    coll = get_collector()
    if coll is None:
        return
    s = settings or get_settings()
    usd = _estimate_cost_usd(model, input_tokens, output_tokens, s)
    coll.ledger.append(
        {
            "ts": utc_iso(),
            "agent": agent,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost_usd": round(usd, 6),
        }
    )


def ledger_totals(entries: list[dict[str, Any]]) -> dict[str, Any]:
    tin = sum(int(e.get("input_tokens", 0)) for e in entries)
    tout = sum(int(e.get("output_tokens", 0)) for e in entries)
    usd = sum(float(e.get("estimated_cost_usd", 0)) for e in entries)
    return {"total_input_tokens": tin, "total_output_tokens": tout, "total_estimated_cost_usd": round(usd, 4)}
