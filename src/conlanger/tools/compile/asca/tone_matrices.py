"""Attach and merge ASCA feature matrices (tickets 62, 124)."""

from __future__ import annotations

import re

# Merge any adjacent feature matrices on the same host (``][`` between brackets).
_ADJACENT_MATRIX_RE = re.compile(r"\[([^\]]*)\]\[([^\]]+)\]")
# Segment / grouping / set close immediately followed by a tone matrix (no colon).
# Exclude U+02D0 (ː) so intervening length marks are left for length_marks.
_BARE_TONE_ATTACH_RE = re.compile(
    r"(?<=[A-Za-z0-9}\)%ʷʲʰʼ"
    r"\u02b0-\u02cf\u02d1-\u02ff"
    r"\u0300-\u036f])\[(tone:\s*[0-9]+)\]",
)


def merge_adjacent_feature_matrices(text: str) -> str:
    """Merge ``…[featuresA][featuresB]…`` into one comma-joined matrix.

    Does not merge across segment hosts (e.g. ``V:[+long] C:[+spread]`` unchanged).
    """
    if not text or "][" not in text:
        return text

    def merge_adjacent(match: re.Match[str]) -> str:
        first, second = match.group(1), match.group(2)
        if first.strip():
            return f"[{first.rstrip()}, {second}]"
        return f"[{second}]"

    prev = None
    while prev != text:
        prev = text
        text = _ADJACENT_MATRIX_RE.sub(merge_adjacent, text)
    return text


def normalize_asca_adjacent_feature_matrices(text: str) -> str:
    """Compile pass: merge adjacent feature matrices on I/O fields (ticket 124)."""
    return merge_adjacent_feature_matrices(text)


def normalize_asca_tone_matrices(text: str) -> str:
    """Merge adjacent ``[tone: N]`` into prior matrices and ensure ``seg:[tone: N]``.

    ASCA rejects incomplete adjacent tone matrices (``V:[+long][tone: 51]``) and
    bare attachments without a colon on substitution output (``V[tone: 5]``).
    Negated Index tone (``[-tone]``) is left untouched upstream.
    """
    if not text:
        return text
    if "[tone:" in text:
        text = merge_adjacent_feature_matrices(text)
        text = _BARE_TONE_ATTACH_RE.sub(r":[\1]", text)
    return text
