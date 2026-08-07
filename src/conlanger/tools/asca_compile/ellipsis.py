"""Index optional grouping ellipsis → ASCA zero-or-more / skip forms."""

import re

_ELLIPSIS = "\u2026"
_ELLIPSIS_SRC = rf"(?:{_ELLIPSIS}|\.\.\.?)"
# Index ``(C…)`` / ``(VC…)`` / ``(C…?)`` → ASCA ``(C,0)`` (zero-or-more).
_TRAILING_GROUPING_ELLIPSIS_RE = re.compile(rf"\(([A-Z$%#]+){_ELLIPSIS_SRC}\??\)")
# Index ``(…X)`` (“for any number of X remaining”) → ASCA ``(..)X``.
_LEADING_GROUPING_ELLIPSIS_RE = re.compile(rf"\({_ELLIPSIS_SRC}([A-Z$%#]+)\)")
_HAS_GROUPING_ELLIPSIS_RE = re.compile(
    rf"\((?:{_ELLIPSIS_SRC}[A-Z$%#]+|[A-Z$%#]+{_ELLIPSIS_SRC}\??)\)"
)


def normalize_asca_optional_grouping_ellipsis(text: str) -> str:
    """Map Index grouping ellipsis in optionals to ASCA zero-or-more / skip forms."""
    if not text or not _HAS_GROUPING_ELLIPSIS_RE.search(text):
        return text

    parts: list[str] = []
    for segment in re.split(r"(\[[^\]]*\])", text):
        if not segment:
            continue
        if segment.startswith("[") and segment.endswith("]"):
            parts.append(segment)
        else:
            segment = _TRAILING_GROUPING_ELLIPSIS_RE.sub(r"(\1,0)", segment)
            segment = _LEADING_GROUPING_ELLIPSIS_RE.sub(r"(..)\1", segment)
            parts.append(segment)
    return "".join(parts)
