"""Embedding cosine vs tonality exemplars (needs OpenAI)."""

from __future__ import annotations

from aiuthor.config.settings import Settings, get_settings
from aiuthor.rag.embeddings import embed_texts
from aiuthor.tonality.presets import TONALITY_PRESETS, normalize_tonality


def tonality_fidelity_score(
    markdown: str,
    target_tonality: str,
    *,
    settings: Settings | None = None,
) -> tuple[float, str]:
    s = settings or get_settings()
    tid = normalize_tonality(target_tonality)
    exemplars = "\n".join(TONALITY_PRESETS[tid]["example_openings"])
    sample = markdown[:6000]
    if not s.openai_api_key or len(sample) < 200:
        return 0.55, "openai_missing_or_text_short_neutral_score"
    try:
        vecs = embed_texts([sample, exemplars], settings=s)
        import numpy as np

        a = np.array(vecs[0], dtype=np.float64)
        b = np.array(vecs[1], dtype=np.float64)
        cos = float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
        score = max(0.0, min(1.0, (cos + 1.0) / 2.0))
        return score, f"embedding_cosine_mapped preset={tid}"
    except Exception as exc:  # noqa: BLE001
        return 0.5, f"tonality_eval_failed:{exc.__class__.__name__}"
