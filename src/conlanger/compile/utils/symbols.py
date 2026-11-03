"""Index Symbol mark normalization for ASCA-canonical index fields."""

from __future__ import annotations

import re

_LENGTH_MARK = "\u02d0"
_INDEX_SYLLABLE_BOUNDARY_RE = re.compile(rf"%(?!{_LENGTH_MARK})")


def normalize_symbols_for_asca(text: str) -> str:
    """Map Index ``%`` / ``$`` to ASCA boundary ``$`` at compile time."""
    if not text:
        return text
    text = _INDEX_SYLLABLE_BOUNDARY_RE.sub("$", text)
    return text
