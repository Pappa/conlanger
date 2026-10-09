"""Pure string normalizers for env/exception fields (no ``IndexRule`` / parse-pass imports)."""

from __future__ import annotations

import re

_STRESS_CONDITION_RE = re.compile(r"when (?:un)?stressed\b", re.IGNORECASE)
_NEITHER_VOWEL_STRESSED_RE = re.compile(
    r",\s*when neither vowel is stressed\b.*$",
    re.IGNORECASE,
)
_COMMA_BEFORE_STRESS_RE = re.compile(
    r",\s*(?=when (?:un)?stressed\b)",
    re.IGNORECASE,
)
_TRAILING_STRESS_AFTER_HASH_RE = re.compile(
    r"\s+when (?:un)?stressed\b.*$",
    re.IGNORECASE,
)
_PROSE_BEFORE_STRESS_RE = re.compile(
    r"^.*?(when (?:un)?stressed\b.*)$",
    re.IGNORECASE,
)

MEDIAL_BOUNDARY_EXCEPTION = "#_, _#"
_BARE_MEDIAL_ENV_RE = re.compile(r"^\s*medial(?:ly)?\s*,?\s*$", re.IGNORECASE)
_BARE_WHEN_MEDIAL_ENV_RE = re.compile(r"^\s*when\s+medial(?:ly)?\s*$", re.IGNORECASE)
_WHEN_MEDIAL_SUFFIX_RE = re.compile(r"(?:,\s*)?when\s+medial(?:ly)?\s*$", re.IGNORECASE)


def normalize_stress_conditions(text: str) -> tuple[str, list[str]]:
    """Normalize Index stress env prose for ASCA; capture removed trailing prose."""
    captures: list[str] = []
    if not text:
        return text, captures
    neither_match = _NEITHER_VOWEL_STRESSED_RE.search(text)
    if neither_match:
        captures.append(neither_match.group(0).strip().lstrip(","))
        text = _NEITHER_VOWEL_STRESSED_RE.sub("", text).rstrip()
        if text:
            return text, captures
    if not _STRESS_CONDITION_RE.search(text):
        return text, captures
    text = _COMMA_BEFORE_STRESS_RE.sub(" ", text)
    if "#" in text:
        match = _TRAILING_STRESS_AFTER_HASH_RE.search(text)
        if match:
            captures.append(match.group(0).strip())
            text = _TRAILING_STRESS_AFTER_HASH_RE.sub("", text).rstrip()
    elif _STRESS_CONDITION_RE.match(text):
        text = f"_ {text}"
    elif "_" not in text:
        match = _PROSE_BEFORE_STRESS_RE.match(text)
        if match:
            text = f"_ {match.group(1)}"
    return text.strip(), captures


def normalize_medial_env_field(text: str) -> tuple[str, bool]:
    """Normalize Index ``medial`` / ``medially`` env prose for ASCA word-internal focus."""
    if not text:
        return text, False
    stripped = text.strip()
    if _BARE_MEDIAL_ENV_RE.match(stripped) or _BARE_WHEN_MEDIAL_ENV_RE.match(stripped):
        return "_", True
    match = _WHEN_MEDIAL_SUFFIX_RE.search(stripped)
    if match:
        return stripped[: match.start()].rstrip(), True
    return text, False
