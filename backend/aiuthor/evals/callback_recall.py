"""Heuristic callback recall vs indexed callbacks."""

from __future__ import annotations

import re

from aiuthor.evals.markdown_sections import chapter_text_map
from aiuthor.memory.callback_index import CallbackIndex


def _keywords(snippet: str, *, max_kw: int = 6) -> list[str]:
    tokens = re.findall(r"[a-z]{5,}", snippet.lower())
    seen: set[str] = set()
    kw: list[str] = []
    for t in tokens:
        if t not in seen:
            seen.add(t)
            kw.append(t)
        if len(kw) >= max_kw:
            break
    return kw


def callback_recall_score(book_id: str, markdown: str) -> tuple[float, str]:
    cmap = chapter_text_map(markdown)
    if not cmap:
        return 0.5, "body_chapters_not_parsed"
    callbacks = CallbackIndex(book_id).list_all()
    if not callbacks:
        return 0.85, "no_callbacks_registered_skip_high"
    hits = 0
    for cb in callbacks:
        text = cmap.get(cb.from_chapter, "")
        if not text:
            continue
        kws = _keywords(cb.snippet)
        if any(k in text for k in kws):
            hits += 1
    score = hits / max(1, len(callbacks))
    detail = f"callbacks_hit_keywords {hits}/{len(callbacks)}"
    return score, detail
