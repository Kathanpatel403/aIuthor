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
