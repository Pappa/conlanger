"""Index affricate tie bar (U+035C) → ASCA tie (U+0361) (ticket 135).

Index and KneeQuickie often write ``t͜s`` (combining double breve below). ASCA
expects ``t͡s`` (combining double inverted breve). Compile-only; ``raw`` unchanged.
"""

from __future__ import annotations

import re

from conlanger.tools.compile.asca._patterns import IPA_SEGMENT

_INDEX_AFFRICATE_TIE = "\u035c"
_ASCA_AFFRICATE_TIE = "\u0361"
_DANGLING_TIE_RE = re.compile(
    rf"({IPA_SEGMENT}){re.escape(_ASCA_AFFRICATE_TIE)}(?=[,\}}>\s]|$)"
)
_TIE_BEFORE_ASPIRATION_RE = re.compile(
    rf"({IPA_SEGMENT}){re.escape(_ASCA_AFFRICATE_TIE)}(\u02b0)"
)


def normalize_index_affricate_tie_bars(text: str) -> str:
    """Rewrite Index tie-bar affricate notation to ASCA ties."""
    if not text:
        return text
    if _INDEX_AFFRICATE_TIE in text:
        text = text.replace(_INDEX_AFFRICATE_TIE, _ASCA_AFFRICATE_TIE)
    if _ASCA_AFFRICATE_TIE in text:
        text = _TIE_BEFORE_ASPIRATION_RE.sub(r"\1\2", text)
        text = _DANGLING_TIE_RE.sub(r"\1", text)
    return text


__all__ = ["normalize_index_affricate_tie_bars"]
