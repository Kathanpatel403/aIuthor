"""Slice assembler Markdown into logical sections."""

from __future__ import annotations

import re


def extract_body_chunk(markdown: str) -> str:
    if "# Body" not in markdown:
        return ""
    chunk = markdown.split("# Body", 1)[1]
    for stop in ("\n# Afterword", "\n# Appendix"):
        if stop in chunk:
            chunk = chunk.split(stop, 1)[0]
    return chunk


def chapter_text_map(markdown: str) -> dict[int, str]:
    """Map chapter number → lowercase body text (assembler uses `## Chapter N:`)."""
    chunk = extract_body_chunk(markdown)
    pattern = re.compile(r"^## Chapter\s+(\d+):\s*[^\n]*\n", re.MULTILINE)
    matches = list(pattern.finditer(chunk))
    out: dict[int, str] = {}
    for i, m in enumerate(matches):
        num = int(m.group(1))
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(chunk)
        out[num] = chunk[start:end].lower()
    return out


def concatenated_body(markdown: str) -> str:
    cmap = chapter_text_map(markdown)
    return "\n".join(cmap.values()).lower()
