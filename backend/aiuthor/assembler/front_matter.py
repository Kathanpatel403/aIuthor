"""Front matter — fully rendered skeleton (no TBD/PLACEHOLDER visible to reader).

All placeholders that were visible in the exported PDF are replaced with either
real generated text (drawn from the outline) or tasteful stand-ins that make
sense for any book topic.
"""

from __future__ import annotations

from aiuthor.schemas.brief import BookOutline


# Curated epigraphs — rotated by first char of book title so it varies per book
_EPIGRAPHS = [
    ("The beginning of wisdom is the discovery of our own ignorance.", "Will Durant"),
    ("What we know is a drop, what we don't know is an ocean.", "Isaac Newton"),
    ("An investment in knowledge pays the best interest.", "Benjamin Franklin"),
    ("The more I read, the more I acquire, the more certain I am that I know nothing.", "Voltaire"),
    ("Real knowledge is to know the extent of one's ignorance.", "Confucius"),
]


def _pick_epigraph(book_title: str) -> tuple[str, str]:
    idx = ord(book_title[0].upper()) % len(_EPIGRAPHS) if book_title else 0
    return _EPIGRAPHS[idx]


def _chapter_list_prose(outline: BookOutline) -> str:
    """One sentence per chapter woven into the Introduction."""
    lines = []
    for ch in outline.chapters:
        lines.append(f"Chapter {ch.number}, *{ch.title}*, {ch.summary.rstrip('.')}.")
    return "\n\n".join(lines)


def _preface_body(outline: BookOutline) -> str:
    return (
        f"This book grew out of a simple question: what does a thoughtful reader "
        f"actually need to know about {outline.title.lower()}? "
        f"The answer shaped every chapter that follows.\n\n"
        f"Each section is built to stand on its own, yet the arc rewards reading in order. "
        f"Feel free to jump to the chapter that presses hardest on your current situation "
        f"and return to the others when you are ready.\n\n"
        f"The ideas here are grounded in evidence and tested against real-world friction. "
        f"Where the research is unsettled, this book says so plainly."
    )


def _introduction_body(outline: BookOutline) -> str:
    return (
        f"*{outline.title}* is organised into {len(outline.chapters)} chapters. "
        f"Here is what each one covers:\n\n"
        + _chapter_list_prose(outline)
        + f"\n\nBy the final page the reader will have a clear, actionable map "
        f"of {outline.title.lower()} — and the confidence to use it."
    )


def static_front_matter_skeleton(outline: BookOutline | str) -> str:  # type: ignore[override]
    """
    Accepts either a BookOutline (preferred) or a bare book_title string
    for backwards-compatibility with callers that pass only the title.
    """
    if isinstance(outline, str):
        # Legacy call — minimal enrichment possible
        title = outline
        epigraph_text, epigraph_attr = _pick_epigraph(title)
        return f"""# Half-title
*{title}*

# Title Page
**{title}**

First Edition

# Dedication
*To every reader who decided that understanding matters.*

# Epigraph
> "{epigraph_text}"
> — {epigraph_attr}

# Contents
<!--TOC_PLACEHOLDER-->

# Preface
This book grew out of a simple question: what does a reader genuinely need to know?
The answer shaped everything that follows.

Each chapter stands on its own, yet the arc rewards reading in order.
The ideas are grounded in evidence and tested against real-world friction.

# Introduction
The chapters ahead build a complete picture from first principles.
By the final page you will have a clear, actionable framework — and the confidence to use it.
"""

    # Rich call with full outline
    epigraph_text, epigraph_attr = _pick_epigraph(outline.title)
    return f"""# Half-title
*{outline.title}*

# Title Page
**{outline.title}**

{f'*{outline.subtitle}*' if outline.subtitle else ''}

First Edition

# Dedication
*To every reader who decided that understanding matters.*

# Epigraph
> "{epigraph_text}"
> — {epigraph_attr}

# Contents
<!--TOC_PLACEHOLDER-->

# Preface
{_preface_body(outline)}

# Introduction
{_introduction_body(outline)}
"""


def toc_from_chapters(chapters: list[tuple[int, str]]) -> str:
    lines: list[str] = []
    for num, title in chapters:
        lines.append(f"- Chapter {num}: {title}")
    return "\n".join(lines) + "\n"
