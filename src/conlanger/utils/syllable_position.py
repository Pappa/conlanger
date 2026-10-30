"""Parse-time editorial normalisation for Index syllable position markers."""

from __future__ import annotations

import re

_EDITORIAL_IN_RE = re.compile(
    r"^in\s+(#U(?:\s*,\s*U#)?|U#)\s*$",
    re.IGNORECASE,
)
_COMMA_U_HASH_RE = re.compile(r"^#U\s*,\s*U#$")


def strip_editorial_in_before_syllable_position(text: str) -> str:
    """Strip Index editorial ``in`` before mechanical ``#U`` / ``U#`` markers."""
    stripped = text.strip()
    match = _EDITORIAL_IN_RE.match(stripped)
    if not match:
        return text
    marker = match.group(1)
    if _COMMA_U_HASH_RE.fullmatch(marker):
        return "#U, U#"
    return marker
