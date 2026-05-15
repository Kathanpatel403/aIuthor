"""Minimal PDF export (fpdf2) — English/Latin-1 friendly."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF


def markdownish_to_pdf(text: str, out_path: Path) -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    for block in text.replace("\r\n", "\n").split("\n\n"):
        for line in block.split("\n"):
            safe = "".join(c if ord(c) < 128 else "?" for c in line)
            if line.startswith("# "):
                pdf.set_font("Helvetica", "B", 14)
                pdf.multi_cell(0, 8, safe[2:].strip())
                pdf.ln(2)
                pdf.set_font("Helvetica", size=10)
            elif line.startswith("## "):
                pdf.set_font("Helvetica", "B", 12)
                pdf.multi_cell(0, 7, safe[3:].strip())
                pdf.ln(1)
                pdf.set_font("Helvetica", size=10)
            elif line.startswith("### "):
                pdf.set_font("Helvetica", "B", 11)
                pdf.multi_cell(0, 6, safe[4:].strip())
                pdf.ln(1)
                pdf.set_font("Helvetica", size=10)
            else:
                pdf.multi_cell(0, 5, safe)
        pdf.ln(2)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
