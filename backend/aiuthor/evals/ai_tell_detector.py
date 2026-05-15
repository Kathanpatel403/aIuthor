"""Regex + lightweight heuristic AI-tell detection."""

from __future__ import annotations

from aiuthor.humanizer.rules import list_violations


def ai_tell_score(markdown: str) -> tuple[float, str]:
    v = list_violations(markdown)
    # Penalize roughly ~12% per violation, floor at 0
    penalty = min(1.0, len(v) * 0.12)
    score = max(0.0, 1.0 - penalty)
    detail = f"{len(v)} deterministic violations; samples: {v[:6]}"
    return score, detail
