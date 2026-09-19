"""Attach and merge ASCA feature matrices (tickets 62, 124, 133)."""

from __future__ import annotations

import re

# Merge any adjacent feature matrices on the same host (``][`` between brackets).
_ADJACENT_MATRIX_RE = re.compile(r"\[([^\]]*)\]\[([^\]]+)\]")
# Colon-chained matrices on one host (``:[featuresA]:[featuresB]``).
_COLON_CHAINED_MATRIX_RE = re.compile(r":\[([^\]]*)\]:\[([^\]]+)\]")
# Segment / grouping / set close immediately followed by a tone matrix (no colon).
# Exclude U+02D0 (ː) so intervening length marks are left for length_marks.
_BARE_TONE_ATTACH_RE = re.compile(
    r"(?<=[A-Za-z0-9}\)%ʷʲʰʼ"
    r"\u02b0-\u02cf\u02d1-\u02ff"
    r"\u0300-\u036f])\[(tone:\s*[0-9]+)\]",
)


def _merge_matrix_pair(first: str, second: str) -> str:
    if first.strip():
        return f"[{first.rstrip()}, {second}]"
    return f"[{second}]"


def merge_adjacent_feature_matrices(text: str) -> str:
    """Merge adjacent or colon-chained feature matrices on one host.

    ``…[featuresA][featuresB]…`` and ``…:[featuresA]:[featuresB]…`` become one
    comma-joined matrix. Does not merge across segment hosts (e.g.
    ``V:[+long] C:[+spread]`` unchanged).
    """
    if not text or ("][" not in text and "]:[" not in text):
        return text

    def merge_bracket_adjacent(match: re.Match[str]) -> str:
        return _merge_matrix_pair(match.group(1), match.group(2))

    def merge_colon_chained(match: re.Match[str]) -> str:
        return ":" + _merge_matrix_pair(match.group(1), match.group(2))

    prev = None
    while prev != text:
        prev = text
        text = _ADJACENT_MATRIX_RE.sub(merge_bracket_adjacent, text)
        text = _COLON_CHAINED_MATRIX_RE.sub(merge_colon_chained, text)
    return text


def normalize_asca_adjacent_feature_matrices(text: str) -> str:
    """Compile pass: merge adjacent / colon-chained matrices (tickets 124, 133)."""
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
