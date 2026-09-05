"""Index prenasal ⁿ prefix → ASCA nasal + segment (ticket 117).

Index uses Unicode superscript ``ⁿ`` (U+207F) as a prenasal prefix on class
letters and IPA segments. ASCA does not resolve bare ``ⁿ`` but accepts the
two-segment form ``N`` + consonant, or literal prenasal graphemes ``ⁿd`` and
``ⁿt``.

Transforms (compile layer only; index ``raw`` unchanged per ADR-0010):

| Pattern | Example | Expansion |
|---------|---------|-----------|
| Class prefix | ``ⁿP`` | ``N P`` |
| Class infix | ``VⁿP`` | ``V N P`` |
| IPA prefix | ``ⁿs``, ``ⁿʃ`` | ``N s``, ``N ʃ`` |
| Literal grapheme | ``ⁿd``, ``ⁿt`` | unchanged |
"""

from __future__ import annotations

import re

from conlanger.tools.compile.asca._patterns import IPA_SEGMENT

_PRENASAL = "\u207f"
_VALID_PRENASAL_GRAPHEMES = frozenset({"ⁿd", "ⁿt"})
_BOUNDARY = r"(?:^|(?<=[\{{,\s/_(#>|]))"
_CLASS_FOLLOW = r"(?=[:\[,\]\{{\}}\s/>_#$%|!\)-]|$|[a-z\u0250-\u02af])"

_CLASS_INFIX_RE = re.compile(rf"([A-Z]){_PRENASAL}([A-Z])")
_CLASS_PREFIX_RE = re.compile(rf"{_BOUNDARY}(?<!\(){_PRENASAL}([A-Z]){_CLASS_FOLLOW}")
_IPA_PREFIX_RE = re.compile(rf"{_BOUNDARY}(?<!\(){_PRENASAL}({IPA_SEGMENT})(?![+:\w])")


def _expand_ipa_prenasal(match: re.Match[str]) -> str:
    segment = match.group(1)
    grapheme = f"{_PRENASAL}{segment}"
    if grapheme in _VALID_PRENASAL_GRAPHEMES:
        return grapheme
    return f"N {segment}"


def _rewrite_outside_brackets(text: str) -> str:
    parts: list[str] = []
    for segment in re.split(r"(\[[^\]]*\])", text):
        if not segment:
            continue
        if segment.startswith("[") and segment.endswith("]"):
            parts.append(segment)
            continue
        segment = _CLASS_INFIX_RE.sub(r"\1 N \2", segment)
        segment = _CLASS_PREFIX_RE.sub(r"N \1", segment)
        segment = _IPA_PREFIX_RE.sub(_expand_ipa_prenasal, segment)
        parts.append(segment)
    return "".join(parts)


def normalize_prenasal_prefix(text: str) -> str:
    """Expand Index ``ⁿ`` prenasal prefix notation to ASCA-legal segments."""
    if not text or _PRENASAL not in text:
        return text
    return _rewrite_outside_brackets(text)


__all__ = ["normalize_prenasal_prefix"]
