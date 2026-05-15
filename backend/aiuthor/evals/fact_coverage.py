"""Rough overlap between registry facts and generated body text."""

from __future__ import annotations

import re

from aiuthor.evals.markdown_sections import concatenated_body
from aiuthor.memory.fact_registry import FactRegistry


def fact_coverage_score(book_id: str, markdown: str) -> tuple[float, str]:
    facts = FactRegistry(book_id).list_all()
    body = concatenated_body(markdown)
    if not facts:
        return 0.75, "no_facts_in_registry_neutral_high"
    if len(body) < 50:
        return 0.4, "body_too_short_for_coverage_check"
    hits = 0
    for f in facts:
        words = re.findall(r"[a-z]{5,}", f.claim_text.lower())
        uniq = list(dict.fromkeys(words))[:8]
        if any(w in body for w in uniq):
            hits += 1
    score = hits / len(facts)
    detail = f"facts_with_keyword_echo {hits}/{len(facts)}"
    return score, detail
