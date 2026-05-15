"""Map (surface, tonality) → system-prompt modifier for every book surface (Phase 4)."""

from __future__ import annotations

from aiuthor.tonality.presets import TONALITY_PRESETS, TonalityId, normalize_tonality

SURFACE_DESCRIPTIONS: dict[str, str] = {
    "chapter_body": "Main narrative or explanatory chapter prose.",
    "preface": "Author-facing note to the reader before the body.",
    "foreword": "Guest or author introduction framing why this book exists now.",
    "introduction": "Sets stakes, audience, and roadmap; first arabic-numbered entry point.",
    "glossary_definition": "Short definition line in glossary entries.",
    "about_author": "Bio blurb; third person unless tonality forbids.",
    "back_cover_copy": "Marketing copy on the back cover; tight and scannable.",
    "afterword": "Reflective closing note tying themes together.",
    "acknowledgments": "Credit collaborators and sources; keep sincere.",
}


def cascade_system_modifier(surface: str, tonality: str) -> str:
    """
    Returns a block to append to SYSTEM instructions so tone applies to non-body surfaces too.
    """
    tid: TonalityId = normalize_tonality(tonality)
    cfg = TONALITY_PRESETS[tid]
    surf = SURFACE_DESCRIPTIONS.get(surface, surface.replace("_", " "))
    sp = (
        "You may use second-person ('you') where it helps clarity."
        if cfg["second_person_ok"]
        else "Prefer third person or neutral instructional voice; avoid direct 'you' unless quoting."
    )
    openings = "\n".join(f"- {o}" for o in cfg["example_openings"][:2])
    return (
        f"## Tonality: {cfg['label']}\n"
        f"**Surface:** {surface} — {surf}\n"
        f"**Reader address:** {sp}\n"
        f"**Rhythm:** {cfg['rhythm_notes']}\n"
        f"**Vocabulary:** {cfg['vocabulary']}\n"
        f"**Hooks:** {cfg['hook_style']}\n"
        f"**Avoid:** {cfg['banned_softeners']}\n"
        f"**Example openings (voice only, do not copy verbatim):**\n{openings}\n"
    )
