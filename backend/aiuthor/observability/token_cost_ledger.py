"""OpenAI chat usage → USD estimates (configurable via Settings)."""

from __future__ import annotations

from typing import Any

from aiuthor.config.settings import Settings, get_settings
from aiuthor.observability.context import get_collector, utc_iso


def _estimate_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    settings: Settings,
) -> float:
    """Rough public-list pricing; override via env if OpenAI changes rates."""
    ml = model.lower()
    mini_id = settings.openai_chat_model_mini.lower()
    primary_id = settings.openai_chat_model.lower()
    if ml == mini_id:
        inp_rate = settings.price_openai_mini_input_per_mtok
        out_rate = settings.price_openai_mini_output_per_mtok
    elif ml == primary_id:
        inp_rate = settings.price_openai_primary_input_per_mtok
        out_rate = settings.price_openai_primary_output_per_mtok
    else:
        # Best-effort tier for snapshot / FT ids not matching configured names exactly
        if "mini" in ml and ("gpt-4" in ml or "4o" in ml):
            inp_rate = settings.price_openai_mini_input_per_mtok
            out_rate = settings.price_openai_mini_output_per_mtok
        else:
            inp_rate = settings.price_openai_primary_input_per_mtok
            out_rate = settings.price_openai_primary_output_per_mtok
    return (input_tokens / 1_000_000.0) * inp_rate + (output_tokens / 1_000_000.0) * out_rate


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
