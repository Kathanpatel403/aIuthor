"""Verify required structural headings exist (assembler contract)."""

from __future__ import annotations

REQUIRED_MARKERS: tuple[str, ...] = (
    "# Half-title",
    "# Title Page",
    "# Dedication",
    "# Epigraph",
    "# Contents",
    "# Foreword",
    "# Preface",
    "# Acknowledgments",
    "# Introduction",
    "# Body",
    "# Afterword",
    "# Appendix",
    "# Glossary",
    "# References",
    "# About the Author",
    "# Back Cover Copy",
)


REQUIRED_SECTION_IDS: tuple[str, ...] = tuple(
    m.strip("# ").lower().replace(" ", "-") for m in REQUIRED_MARKERS
)


def structural_score(markdown: str) -> tuple[float, str, list[str]]:
    md = markdown.replace("\r\n", "\n")
    missing: list[str] = []
    for marker in REQUIRED_MARKERS:
        if marker not in md:
            missing.append(marker.strip("# "))
    hit = len(REQUIRED_MARKERS) - len(missing)
    score = hit / len(REQUIRED_MARKERS)
    detail = f"{hit}/{len(REQUIRED_MARKERS)} structural headings present"
    return score, detail, missing


def structural_score_html(html: str) -> tuple[float, str, list[str]]:
    """Match assembler HTML section ids to required structural surfaces."""
    missing: list[str] = []
    for marker, sid in zip(REQUIRED_MARKERS, REQUIRED_SECTION_IDS, strict=True):
        label = marker.strip("# ")
        if sid == "body":
            if 'class="chapter"' not in html and "class='chapter'" not in html:
                missing.append(label)
            continue
        if f'id="{sid}"' not in html and f"id='{sid}'" not in html:
            missing.append(label)
    hit = len(REQUIRED_MARKERS) - len(missing)
    score = hit / len(REQUIRED_MARKERS)
    detail = f"{hit}/{len(REQUIRED_MARKERS)} structural sections present (HTML)"
    return score, detail, missing
