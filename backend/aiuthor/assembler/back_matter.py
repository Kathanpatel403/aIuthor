"""Back matter Markdown + glossary from concept bible."""

from __future__ import annotations

from aiuthor.memory import ConceptBible


def glossary_markdown(book_id: str) -> str:
    lines = ["# Glossary", ""]
    for c in ConceptBible(book_id).list_all():
        lines.append(f"**{c.term}**  ")
        lines.append(f"{c.definition}\n")
    if len(lines) <= 2:
        lines.append("_No indexed terms yet._\n")
    return "\n".join(lines)


def static_back_matter(book_title: str, book_id: str) -> str:
    return f"""# Afterword
Closing reflections on what comes next for the reader after {book_title}.

# Appendix
Sample worksheets / checklists — placeholder section.

{glossary_markdown(book_id)}

# References
Include only sources that were retrieved during research for this run. Do not fabricate academic citations or book titles.

# About the Author
The author writes with a bias toward systems, kindness, and practical next steps.

# Back Cover Copy
**{book_title}** — one positioning sentence, three concrete benefit bullets, and a warm call to action.
"""
