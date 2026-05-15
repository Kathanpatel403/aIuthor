"""Humanizer banned phrases / patterns (must mirror prompts dossier)."""

from __future__ import annotations

import re

# Exact phrases (case-insensitive substring match after lowercasing)
BANNED_PHRASES: tuple[str, ...] = (
    "it's important to note",
    "it is important to note",
    "delve into",
    "in today's fast-paced world",
    "the landscape of",
    "at the end of the day",
    "leverage synergies",
    "robust framework",
    "unlock the power",
    "game-changer",
    "deep dive",
    "holistic approach",
    "paradigm shift",
    "cutting-edge",
    "moving forward",
    "first and foremost",
    "needless to say",
)

# Regex patterns (AI-tell mechanical structures)
BANNED_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bnot only\b.{0,80}\bbut also\b", re.I | re.S),
    re.compile(r"\bfirstly\b.*\bsecondly\b.*\bthirdly\b", re.I | re.S),
)


def list_violations(text: str) -> list[str]:
    t = text.lower()
    hits: list[str] = []
    for p in BANNED_PHRASES:
        if p in t:
            hits.append(f"banned_phrase:{p}")
    for rx in BANNED_PATTERNS:
        if rx.search(text):
            hits.append(f"banned_pattern:{rx.pattern[:48]}")
    return hits
