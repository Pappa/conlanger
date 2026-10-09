"""Residual output/environment boundary fixes (ticket 82).

Index sometimes glues a deletion column onto a set or matrix (``}∅``)
without a segment boundary. ASCA then reports a missing ``/`` between
output and environment. Drop the glued ``∅`` — the same mixed-column
null policy as ticket 60, applied when the null was concatenated
instead of space-separated.
"""

from __future__ import annotations

import re

_CONCAT_NULL_RE = re.compile(r"([}\])])∅")


def drop_concatenated_deletion_column(text: str) -> str:
    """Drop a deletion ``∅`` concatenated onto a set, matrix, or group closer."""
    if not text or "∅" not in text:
        return text
    return _CONCAT_NULL_RE.sub(r"\1", text)
