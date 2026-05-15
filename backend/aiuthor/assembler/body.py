"""Concatenate chapter bodies."""

from __future__ import annotations


def body_markdown(chapters: list[tuple[int, str, str]]) -> str:
    parts: list[str] = ["# Body", ""]
    for num, title, body in chapters:
        parts.append(f"## Chapter {num}: {title}\n\n")
        parts.append(body.strip())
        parts.append("\n\n")
    return "".join(parts)
