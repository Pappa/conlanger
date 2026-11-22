"""Pure string normalizers for env/exception fields (no ``IndexRule`` / parse-pass imports)."""

from __future__ import annotations

import re

_NEITHER_VOWEL_STRESSED_RE = re.compile(
    r",\s*when neither vowel is stressed\b.*$",
    re.IGNORECASE,
)
_STRESS_TAIL_CAPTURE_RE = re.compile(
    r"(?:,\s*|\s+)(?P<tail>when (?:un)?stressed\b.*)$",
    re.IGNORECASE,
)
_BARE_WHOLE_STRESS_ENV_RE = re.compile(
    r"^\s*when (?:un)?stressed\b.*$",
    re.IGNORECASE,
)
_UNSTRESSED_TAIL_RE = re.compile(r"when\s+unstressed\b", re.IGNORECASE)

MEDIAL_BOUNDARY_EXCEPTION = "#_, _#"
_BARE_MEDIAL_ENV_RE = re.compile(r"^\s*medial(?:ly)?\s*,?\s*$", re.IGNORECASE)
_BARE_WHEN_MEDIAL_ENV_RE = re.compile(r"^\s*when\s+medial(?:ly)?\s*$", re.IGNORECASE)
_WHEN_MEDIAL_SUFFIX_RE = re.compile(r"(?:,\s*)?when\s+medial(?:ly)?\s*$", re.IGNORECASE)


def normalize_stress_conditions(text: str) -> tuple[str, list[str], str | None]:
    """Strip env stress prose to comment; return optional ``[±stress]`` for rule input."""
    captures: list[str] = []
    if not text:
        return text, captures, None

    neither_match = _NEITHER_VOWEL_STRESSED_RE.search(text)
    if neither_match:
        captures.append(neither_match.group(0).strip().lstrip(",").strip())
        text = _NEITHER_VOWEL_STRESSED_RE.sub("", text).rstrip()
        return text, captures, None

    if _BARE_WHOLE_STRESS_ENV_RE.match(text.strip()):
        return text, captures, None

    match = _STRESS_TAIL_CAPTURE_RE.search(text)
    if not match:
        return text.strip(), captures, None

    tail = match.group("tail").strip()
    captures.append(tail)
    text = text[: match.start()].rstrip().rstrip(",").strip()

    input_matrix = "[-stress]" if _UNSTRESSED_TAIL_RE.search(tail) else "[+stress]"
    return text, captures, input_matrix


def normalize_medial_env_field(text: str) -> tuple[str, bool]:
    """Normalize Index ``medial`` / ``medially`` env prose for ASCA word-internal focus."""
    if not text:
        return text, False
    stripped = text.strip()
    if _BARE_MEDIAL_ENV_RE.match(stripped) or _BARE_WHEN_MEDIAL_ENV_RE.match(stripped):
        return "", True
    match = _WHEN_MEDIAL_SUFFIX_RE.search(stripped)
    if match:
        return stripped[: match.start()].rstrip(), True
    return text, False
