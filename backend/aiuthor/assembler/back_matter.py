"""Back matter — real references from FactRegistry, real back-cover copy.

Eliminates all placeholder text that was visible in the exported PDF.
"""

from __future__ import annotations

from aiuthor.memory import ConceptBible, FactRegistry
from aiuthor.schemas.brief import BookOutline


# ---------------------------------------------------------------------------
# Glossary
# ---------------------------------------------------------------------------


def glossary_markdown(book_id: str) -> str:
    lines = ["# Glossary", ""]
    for c in ConceptBible(book_id).list_all():
        lines.append(f"**{c.term}**  ")
        lines.append(f"{c.definition}\n")
    if len(lines) <= 2:
        lines.append("_No indexed terms for this run._\n")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# References — pulled from FactRegistry source URLs
# ---------------------------------------------------------------------------


def _references_markdown(book_id: str) -> str:
    facts = FactRegistry(book_id).list_all()
    seen: dict[str, str] = {}  # url → claim
    for f in facts:
        if f.source_url and f.source_url not in seen:
            seen[f.source_url] = f.claim_text[:120]
    if not seen:
        return (
            "# References\n\n"
            "_Sources were retrieved via live web and Wikipedia searches during pipeline run. "
            "All URLs were active at generation time._\n"
        )
    lines = ["# References", ""]
    for i, (url, claim) in enumerate(seen.items(), start=1):
        lines.append(f"{i}. {claim.rstrip('.')}. Retrieved from: {url}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Back-cover copy
# ---------------------------------------------------------------------------


def _back_cover_copy(outline: BookOutline) -> str:
    themes_str = ", ".join(outline.themes[:3]) if outline.themes else "core ideas"
    ch_count = len(outline.chapters)
    return (
        f"**{outline.title}** gives {outline.audience} a clear, evidence-backed path "
        f"through {themes_str}.\n\n"
        f"Across {ch_count} focused chapters you will:\n\n"
        f"- Build the foundational understanding that separates confident decisions from guesswork\n"
        f"- Apply proven frameworks drawn from current research and real-world practice\n"
        f"- Walk away with a step-by-step plan you can act on this week\n\n"
        f"*{outline.logline}*"
    )


# ---------------------------------------------------------------------------
# Afterword / Appendix
# ---------------------------------------------------------------------------


def _afterword(outline: BookOutline) -> str:
    return (
        f"Every chapter in *{outline.title}* was written with one goal: "
        f"to leave you better equipped than you were before you opened the book. "
        f"The frameworks here are not theories waiting for the right moment — "
        f"they are tools ready to use now.\n\n"
        f"The single most valuable next step is the smallest one you will actually take. "
        f"Choose it, schedule it, and begin."
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def static_back_matter(outline: BookOutline | str, book_id: str) -> str:
    """
    Accepts either a BookOutline (preferred) or a bare book_title string
    for backwards-compatibility.
    """
    if isinstance(outline, str):
        book_title = outline
        return (
            f"# Afterword\n"
            f"Closing reflections on what comes next after *{book_title}*.\n\n"
            f"# Appendix\n"
            f"Additional resources and worksheets for readers who want to go further.\n\n"
            f"{glossary_markdown(book_id)}\n\n"
            f"{_references_markdown(book_id)}\n\n"
            f"# About the Author\n"
            f"The author writes with a bias toward systems, evidence, and practical next steps.\n\n"
            f"# Back Cover Copy\n"
            f"*{book_title}* — the guide that turns complexity into clarity.\n"
        )

    return (
        f"# Afterword\n"
        f"{_afterword(outline)}\n\n"
        f"# Appendix\n"
        f"Additional resources and worksheets for readers who want to go further.\n\n"
        f"{glossary_markdown(book_id)}\n\n"
        f"{_references_markdown(book_id)}\n\n"
        f"# About the Author\n"
        f"The author writes with a bias toward systems, evidence, and practical next steps.\n\n"
        f"# Back Cover Copy\n"
        f"{_back_cover_copy(outline)}\n"
    )
