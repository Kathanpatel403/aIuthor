"""DOCX export with simple heading mapping."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.shared import Pt


def markdownish_to_docx(text: str, out_path: Path) -> None:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.size = Pt(11)
    for block in text.replace("\r\n", "\n").split("\n\n"):
        for line in block.split("\n"):
            if line.startswith("# "):
                doc.add_heading(line[2:].strip(), level=0)
            elif line.startswith("## "):
                doc.add_heading(line[3:].strip(), level=1)
            elif line.startswith("### "):
                doc.add_heading(line[4:].strip(), level=2)
            elif line.strip():
                doc.add_paragraph(line.strip())
        doc.add_paragraph("")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))
