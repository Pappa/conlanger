"""Typographic apostrophe → ejective mark."""

import re

from conlanger.tools.asca_compile._patterns import IPA_SEGMENT

_EJECTIVE = "\u02bc"
_TYPO_APOSTROPHE_RE = re.compile(rf"({IPA_SEGMENT}|[A-Z])(\u2019)")


def normalize_typographic_apostrophes(text: str) -> str:
    """Map Index typographic apostrophe (U+2019) to ejective ``ʼ`` (U+02BC)."""
    if not text or "\u2019" not in text:
        return text
    return _TYPO_APOSTROPHE_RE.sub(rf"\1{_EJECTIVE}", text)
