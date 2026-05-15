"""Front matter Markdown skeleton (legal placeholders; pagination refined in PDF builder)."""


def static_front_matter_skeleton(book_title: str) -> str:
    return f"""# Half-title
*{book_title}*

# Title Page
**{book_title}**

Copyright © YEAR TBD. All rights reserved.

ISBN: [PLACEHOLDER — assign before publication]  
Edition: First edition  
Rights: TBD (territory, translation, derivative works)  
CIP Data Block: [Library of Congress placeholder — generate with a qualified librarian]

# Dedication
_To readers building a better relationship with their attention and their money._

# Epigraph
> "Clarity is kindness." — placeholder (replace with verified quote before publication)

# Contents
<!--TOC_PLACEHOLDER-->

# Foreword
*(Optional guest foreword — placeholder.)*

# Preface
This preface orients the reader to the promise of the book and how to use it.

# Acknowledgments
Thanks to early readers, editors, and the sources that grounded the research.

# Introduction
This introduction previews the arc of the book and how each chapter builds on the last.
"""


def toc_from_chapters(chapters: list[tuple[int, str]]) -> str:
    lines: list[str] = []
    for num, title in chapters:
        lines.append(f"- Chapter {num}: {title}")
    return "\n".join(lines) + "\n"
