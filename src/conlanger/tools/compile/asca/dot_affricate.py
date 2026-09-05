"""Index dot-affricate / cluster notation → ASCA segments (ticket 118).

Index uses a single ``.`` between segments (or after a segment) to mark
affricate boundaries, consonant-cluster splits, or morpheme junctures. ASCA
expects ``..`` for range dots and bare segment sequences otherwise.

Transforms (compile layer only; index ``raw`` unchanged per ADR-0010):

| Pattern | Example | Expansion |
|---------|---------|-----------|
| Affricate | ``t.ʃ`` | ``tʃ`` |
| Cluster | ``s.d``, ``n.br`` | ``sd``, ``nbr`` |
| Trailing dot | ``p.``, ``tr.`` | ``p``, ``tr`` |
| After matrix | ``je:[+stress].o`` | ``je:[+stress]o`` |
| Before set | ``s.{ts,pj}`` | ``s{ts,pj}`` |
| Optional tail | ``(ç.)tr`` | ``(ç)tr`` |
| Inside set | ``{s.ts,br}`` | ``{sts,br}`` |

Double-dot range syntax ``..`` is preserved (Yup'ik geminate ranges).
"""

from __future__ import annotations

import re

from conlanger.tools.compile.asca._patterns import IPA_SEGMENT

_RANGE_DOT = "\ue000"  # placeholder while normalising single dots
_INDEX_SEGMENT = rf"(?:{IPA_SEGMENT}|[A-Z])\d*"
_AFTER_FEATURE_MATRIX = re.compile(rf"(\[[^\]]*\])\.(?={_INDEX_SEGMENT})")
_BEFORE_SET = re.compile(rf"({_INDEX_SEGMENT})\.(?=\{{)")
_BEFORE_CLOSE_PAREN = re.compile(rf"({_INDEX_SEGMENT})\.(?=\))")
_BETWEEN_SEGMENTS = re.compile(rf"({_INDEX_SEGMENT})\.(?={_INDEX_SEGMENT}|\()")
_TRAILING_DOT = re.compile(
    rf"({_INDEX_SEGMENT}|\))\."
    r"(?=[\s,}>/%#_!|]|$)"
)


def _protect_range_dots(text: str) -> str:
    return text.replace("..", _RANGE_DOT)


def _restore_range_dots(text: str) -> str:
    return text.replace(_RANGE_DOT, "..")


def _rewrite_outside_brackets(text: str) -> str:
    text = _AFTER_FEATURE_MATRIX.sub(r"\1", text)
    parts: list[str] = []
    for segment in re.split(r"(\[[^\]]*\])", text):
        if not segment:
            continue
        if segment.startswith("[") and segment.endswith("]"):
            parts.append(segment)
            continue
        segment = _BEFORE_SET.sub(r"\1", segment)
        segment = _BEFORE_CLOSE_PAREN.sub(r"\1", segment)
        segment = _BETWEEN_SEGMENTS.sub(r"\1", segment)
        segment = _TRAILING_DOT.sub(r"\1", segment)
        parts.append(segment)
    return "".join(parts)


def normalize_dot_affricate_notation(text: str) -> str:
    """Expand Index single-dot affricate/cluster notation to ASCA segments."""
    if not text or "." not in text:
        return text
    protected = _protect_range_dots(text)
    normalized = _rewrite_outside_brackets(protected)
    return _restore_range_dots(normalized)


__all__ = ["normalize_dot_affricate_notation"]
