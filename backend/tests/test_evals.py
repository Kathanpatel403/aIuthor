"""Structural eval matches assembler headings."""

from aiuthor.evals.structural_check import REQUIRED_MARKERS, structural_score


def test_structural_all_present():
    md = "\n".join(REQUIRED_MARKERS) + "\n# Body\n\n## Chapter 1: Test\n\nhello\n"
    score, _, missing = structural_score(md)
    assert score == 1.0
    assert not missing


def test_structural_detects_gap():
    md = "# Half-title\n"
    score, _, missing = structural_score(md)
    assert score < 1.0
    assert missing


def test_chapter_map_splits_body():
    from aiuthor.evals.markdown_sections import chapter_text_map

    md = """# Body

## Chapter 1: A

alpha

## Chapter 2: B

beta
"""
    cmap = chapter_text_map(md)
    assert 1 in cmap and 2 in cmap
    assert "alpha" in cmap[1]
    assert "beta" in cmap[2]
