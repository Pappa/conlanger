"""Attach ASCA ``[tone: N]`` matrices after length/feature transforms (ticket 62)."""

from __future__ import annotations

import re

# Merge tone into the immediately preceding feature matrix.
_ADJACENT_TONE_RE = re.compile(
    r"\[([^\]]*)\]\[(tone:\s*[0-9]+)\]",
)
# Segment / grouping / set close immediately followed by a tone matrix (no colon).
# Exclude U+02D0 (ː) so intervening length marks are left for length_marks.
_BARE_TONE_ATTACH_RE = re.compile(
    r"(?<=[A-Za-z0-9}\)%ʷʲʰʼ"
    r"\u02b0-\u02cf\u02d1-\u02ff"
    r"\u0300-\u036f])\[(tone:\s*[0-9]+)\]",
)


def normalize_asca_tone_matrices(text: str) -> str:
    """Merge adjacent ``[tone: N]`` into prior matrices and ensure ``seg:[tone: N]``.

    ASCA rejects incomplete adjacent tone matrices (``V:[+long][tone: 51]``) and
    bare attachments without a colon on substitution output (``V[tone: 5]``).
    Negated Index tone (``[-tone]``) is left untouched upstream.
    """
    if not text or "[tone:" not in text:
        return text

    def merge_adjacent(match: re.Match[str]) -> str:
        inner, tone = match.group(1), match.group(2)
        if inner.strip():
            return f"[{inner.rstrip()}, {tone}]"
        return f"[{tone}]"

    prev = None
    while prev != text:
        prev = text
        text = _ADJACENT_TONE_RE.sub(merge_adjacent, text)

    return _BARE_TONE_ATTACH_RE.sub(r":[\1]", text)
