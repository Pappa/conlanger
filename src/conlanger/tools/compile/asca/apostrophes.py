"""Typographic apostrophe → ejective mark."""

import re

from conlanger.tools.asca_compile._patterns import IPA_SEGMENT

_EJECTIVE = "\u02bc"
_CLASS_OR_IPA = rf"({IPA_SEGMENT}|[A-Z])"
_TYPO_APOSTROPHE_RE = re.compile(rf"{_CLASS_OR_IPA}(\u2019)")
_PAREN_TYPO_APOSTROPHE_RE = re.compile(r"(\()\u2019(\))")
_PREFIX_TYPO_APOSTROPHE_RE = re.compile(rf"(^|[\s{{,])\u2019{_CLASS_OR_IPA}")


def normalize_typographic_apostrophes(text: str) -> str:
    """Map Index typographic apostrophe (U+2019) to ejective ``ʼ`` (U+02BC)."""
    if not text or "\u2019" not in text:
        return text
    text = _PAREN_TYPO_APOSTROPHE_RE.sub(rf"\1{_EJECTIVE}\2", text)
    text = _PREFIX_TYPO_APOSTROPHE_RE.sub(
        lambda m: f"{m.group(1)}{m.group(2)}{_EJECTIVE}", text
    )
    return _TYPO_APOSTROPHE_RE.sub(rf"\1{_EJECTIVE}", text)
