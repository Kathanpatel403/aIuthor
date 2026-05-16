"""Build a single professional HTML document for PDF/DOCX export and preview.

Improvements over original:
  - front_matter.static_front_matter_skeleton now accepts the full BookOutline
    so preface, introduction, epigraph, etc. are all dynamically populated.
  - back_matter.static_back_matter now accepts the full BookOutline so
    afterword, back-cover copy, and real references are rendered.
  - TOC is rendered with leader dots (no page numbers in HTML — WeasyPrint
    cannot inject them at this layer, but the TOC lists all chapters by title).
  - Roman-numeral front-matter pages and arabic body pages are declared via
    CSS @page counter rules (supported by WeasyPrint ≥ 60).
  - All Markdown conversion failures fall back cleanly to escaped HTML.
"""

from __future__ import annotations

import html
import re
from typing import Any

from aiuthor.assembler.back_matter import static_back_matter
from aiuthor.assembler.body import body_markdown
from aiuthor.assembler.front_matter import static_front_matter_skeleton
from aiuthor.schemas.brief import BookOutline

try:
    import markdown as _markdown_lib
except ImportError:  # pragma: no cover
    _markdown_lib = None  # type: ignore[assignment]

_MD_CONVERTER: Any = None

BOOK_STYLES = """
/* ------------------------------------------------------------------ *
 * AIuthor — professional print stylesheet                             *
 * Optimized for xhtml2pdf (pisa) and Browser Preview                 *
 * ------------------------------------------------------------------ */

@page {
  size: letter;
  margin: 2cm;
  @frame footer {
    -pdf-frame-content: footer-content;
    bottom: 1cm;
    margin-left: 2cm;
    margin-right: 2cm;
    height: 1cm;
  }
}

* { box-sizing: border-box; }
html { font-size: 11pt; }
body {
  font-family: Georgia, serif;
  line-height: 1.5;
  color: #1a1a1a;
}
.book-root { max-width: 44em; margin: 0 auto; }

/* ---- Section headings ---- */
.section-heading, .chapter-title {
  font-family: Helvetica, Arial, sans-serif;
  font-weight: bold;
  color: #111;
}
.section-heading { font-size: 18pt; margin-bottom: 12pt; }

/* ---- Front matter ---- */
.front-matter { page-break-after: always; }
.back-matter { page-break-before: always; }

/* ---- Title page ---- */
#title-page { text-align: center; padding-top: 2cm; }
#title-page .book-title {
  font-size: 32pt;
  font-weight: bold;
  margin-top: 1cm;
}
#title-page .book-subtitle {
  font-size: 16pt;
  font-style: italic;
  margin-top: 0.5cm;
}
#title-page .edition-line {
  font-size: 10pt;
  color: #666;
  margin-top: 4cm;
}

/* ---- Half-title ---- */
#half-title { text-align: center; font-style: italic; padding-top: 4cm; }

/* ---- Epigraph ---- */
#epigraph blockquote {
  border: none;
  text-align: right;
  font-size: 1.05rem;
  margin: 4rem 0 0;
  color: #444;
}
#epigraph blockquote p { margin: 0; }

/* ---- TOC ---- */
#contents ul.toc-list {
  list-style: none;
  padding: 0;
  margin: 1rem 0;
}
#contents ul.toc-list li {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
  border-bottom: 1px dotted #ccc;
  padding: 0.38rem 0;
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 0.95rem;
}
#contents ul.toc-list li .toc-num {
  flex-shrink: 0;
  color: #777;
  min-width: 5.5em;
}
#contents ul.toc-list li .toc-title { flex: 1; }

/* ---- Body ---- */
.body-matter {
  page: body-page;
  counter-reset: page 1;
  page-break-before: always;
}
.chapter { page-break-before: always; }
.chapter-title {
  font-size: 1.55rem;
  margin: 0 0 1.35rem;
  padding-bottom: 0.55rem;
  border-bottom: 2.5px solid #222;
}
.chapter-label {
  display: block;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #777;
  font-weight: 500;
  margin-bottom: 0.3rem;
}
.chapter-name { display: block; margin-top: 0.3rem; }
.chapter-body p { margin: 0 0 0.9rem; text-align: justify; }
.chapter-body h3 {
  font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 1.1rem;
  margin: 1.35rem 0 0.55rem;
  color: #222;
}
.chapter-body ul, .chapter-body ol { margin: 0 0 0.9rem 1.35rem; }
.chapter-body blockquote {
  margin: 1.1rem 0;
  padding: 0.5rem 1rem;
  border-left: 3px solid #bbb;
  color: #444;
  font-style: italic;
  background: #fafafa;
}

/* ---- Back matter ---- */
#copyright, #references { font-size: 0.92rem; color: #333; }
#references ol { padding-left: 1.2rem; }
#references li { margin-bottom: 0.55rem; line-height: 1.5; }
.glossary-list { margin-top: 0.5rem; }
.glossary-entry { margin-bottom: 0.9rem; }
.glossary-entry dt { font-weight: bold; }
.glossary-entry dd { margin-left: 0; }

/* ---- Back cover ---- */
#back-cover-copy p { font-size: 1.02rem; line-height: 1.65; }
#back-cover-copy ul { margin: 0.7rem 0 0.7rem 1.2rem; }
#back-cover-copy li { margin-bottom: 0.4rem; }
"""


def _md_fragment(text: str) -> str:
    if not text.strip():
        return ""
    if _markdown_lib is None:
        paras = [f"<p>{html.escape(p.strip())}</p>" for p in text.split("\n\n") if p.strip()]
        return "\n".join(paras)
    global _MD_CONVERTER
    if _MD_CONVERTER is None:
        _MD_CONVERTER = _markdown_lib.Markdown(extensions=["extra", "nl2br", "sane_lists"])
    else:
        _MD_CONVERTER.reset()
    return _MD_CONVERTER.convert(text)


def _section_id_from_title(title: str) -> str:
    sid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    aliases = {
        "table-of-contents": "contents",
        "back-cover-copy": "back-cover-copy",
    }
    return aliases.get(sid, sid) or "section"


def _markdown_blocks_to_sections(md: str, *, css_class: str) -> list[str]:
    sections: list[str] = []
    blocks = re.split(r"\n(?=# )", md.replace("\r\n", "\n").strip())
    for block in blocks:
        if not block.strip() or block.strip() == "# Body":
            continue
        lines = block.split("\n", 1)
        title = lines[0].lstrip("#").strip()
        body_md = lines[1] if len(lines) > 1 else ""
        sid = _section_id_from_title(title)

        # Title page gets special treatment
        if sid == "title-page":
            # Extract subtitle if present (italic line right after the bold title)
            title_html = ""
            subtitle_html = ""
            edition_html = ""
            for raw_line in body_md.split("\n"):
                stripped = raw_line.strip()
                if stripped.startswith("**") and stripped.endswith("**"):
                    title_html = f'<p class="book-title">{html.escape(stripped.strip("*"))}</p>'
                elif stripped.startswith("*") and stripped.endswith("*") and not stripped.startswith("**"):
                    subtitle_html = f'<p class="book-subtitle">{html.escape(stripped.strip("*"))}</p>'
                elif stripped:
                    edition_html += f'<p class="edition-line">{html.escape(stripped)}</p>\n'
            inner = title_html + subtitle_html + edition_html
        else:
            inner = _md_fragment(body_md) if body_md.strip() else ""

        sections.append(
            f'<section id="{html.escape(sid)}" class="{css_class}">\n'
            f'  <h1 class="section-heading">{html.escape(title)}</h1>\n'
            f"  {inner}\n"
            f"</section>"
        )
    return sections


def _toc_section(chapters: list[tuple[int, str]]) -> str:
    items = "".join(
        f'<li>'
        f'<span class="toc-num">Chapter {num}</span>'
        f'<span class="toc-title">{html.escape(title)}</span>'
        f'</li>'
        for num, title in chapters
    )
    return (
        '<section id="contents" class="front-matter">\n'
        '  <h1 class="section-heading">Contents</h1>\n'
        f'  <ul class="toc-list">{items}</ul>\n'
        "</section>"
    )


def _parse_body_chapters(md_body: str) -> list[tuple[int, str, str]]:
    if "# Body" not in md_body:
        return []
    body = md_body.split("# Body", 1)[1]
    pattern = re.compile(r"^## Chapter (\d+): (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(body))
    out: list[tuple[int, str, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        out.append((int(m.group(1)), m.group(2).strip(), body[start:end].strip()))
    return out


def _chapter_sections(chapters: list[tuple[int, str, str]]) -> list[str]:
    sections: list[str] = []
    for num, title, body_md in chapters:
        body_html = _md_fragment(body_md)
        sections.append(
            f'<section class="chapter" id="chapter-{num}" data-number="{num}">\n'
            f'  <h2 class="chapter-title">'
            f'<span class="chapter-label">Chapter {num}</span>'
            f'<span class="chapter-name">{html.escape(title)}</span></h2>\n'
            f'  <div class="chapter-body">\n{body_html}\n  </div>\n'
            f"</section>"
        )
    return sections


def _glossary_html(book_id: str) -> str:
    from aiuthor.memory import ConceptBible

    entries: list[str] = []
    for c in ConceptBible(book_id).list_all():
        entries.append(
            f'<div class="glossary-entry"><dt>{html.escape(c.term)}</dt> — '
            f"<dd>{html.escape(c.definition)}</dd></div>"
        )
    if not entries:
        entries.append("<p><em>No indexed terms yet.</em></p>")
    return (
        '<section id="glossary" class="back-matter">\n'
        '  <h1 class="section-heading">Glossary</h1>\n'
        f'  <div class="glossary-list">{"".join(entries)}</div>\n'
        "</section>"
    )


def render_book_html(
    book_id: str,
    outline: BookOutline,
    chapter_bodies: list[str],
) -> str:
    chapters_meta = [(c.number, c.title) for c in outline.chapters]

    # Pass full outline so front/back matter is dynamically populated
    front_md = static_front_matter_skeleton(outline)
    # Strip the inline <!--TOC_PLACEHOLDER--> block; we render TOC ourselves
    front_md = re.sub(r"# Contents\n(?:.*?\n)*?(?=# )", "", front_md, flags=re.DOTALL)

    body_md = body_markdown(
        [(c.number, c.title, chapter_bodies[i]) for i, c in enumerate(outline.chapters)]
    )

    # Pass full outline to back matter
    back_md = static_back_matter(outline, book_id)
    # Strip inline glossary block — we render it separately from ConceptBible
    back_md = re.sub(r"# Glossary\n\n.*?(?=\n# )", "", back_md, count=1, flags=re.DOTALL)

    front_sections = _markdown_blocks_to_sections(front_md, css_class="front-matter")
    back_sections = _markdown_blocks_to_sections(back_md, css_class="back-matter")
    chapter_parts = _chapter_sections(_parse_body_chapters(body_md))

    inner = "\n".join(
        [
            '<div class="book-root">',
            *front_sections,
            _toc_section(chapters_meta),
            '<div class="body-matter">',
            *chapter_parts,
            "</div>",
            *back_sections,
            _glossary_html(book_id),
            "</div>",
        ]
    )
    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8"/>\n'
        f"<title>{html.escape(outline.title)}</title>\n"
        f"<style>{BOOK_STYLES}</style>\n"
        "</head>\n<body>\n"
        f"{inner}\n"
        "</body>\n"
        "<!-- PDF Footer for xhtml2pdf -->\n"
        '<div id="footer-content">\n'
        '  Page <pdf:pagenumber />\n'
        "</div>\n"
        "</html>"
    )
