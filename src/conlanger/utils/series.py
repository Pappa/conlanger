"""In-memory correspondence-series apply/classify (no CSV I/O)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Correspondence-series index: concrete segment base + ordinal subscript (not ₀, not ₓ).
_CORRESPONDENCE_INDEX_RE = re.compile(r"(?<![A-Z])([a-zA-Zæøåɑɡɢ]+)([₁₂₃₄₅₆₇₈₉])")
_COLLECTIVE_TOKEN_RE = re.compile(r"(?<![A-Z])([a-zA-Z]+)ₓ")
_POSITIONAL_SLOT_RE = re.compile(r"^[A-Z][₁₂₃₄₅₆₇₈₉]$")
_IDENTITY_SUBSCRIPT_RE = re.compile(r"^[A-Za-z]₀$")
# ASCA grouping letters cannot host a digit suffix (s1 → S + reference 1).
_ASCA_GROUPING_LETTERS = frozenset("CSOPFLNGV")

_SUBSCRIPT_TO_ASCII = str.maketrans("₁₂₃₄₅₆₇₈₉", "123456789")

# Any token containing an Index subscript digit/letter (includes compounds like ``eh₂``, ``CV₁``).
_SUBSCRIPT_TOKEN_RE = re.compile(r"[A-Za-zæøåɑɡɢ]*[₀₁₂₃₄₅₆₇₈₉ₓ]+")


@dataclass(frozen=True)
class SeriesMapping:
    section_index: str
    token: str
    asca_target: str
    source: str = ""
    notes: str = ""


def classify_subscript_token(token: str) -> str:
    """Classify a subscript-bearing token for coverage accounting."""
    if is_identity_subscript_token(token):
        return "identity"
    if is_positional_slot_token(token):
        return "positional"
    if is_collective_subscript_token(token):
        return "collective"
    if is_correspondence_series_token(token):
        return "correspondence"
    if _CORRESPONDENCE_INDEX_RE.search(token):
        return "compound"
    if "ₓ" in token or "₀" in token or re.search(r"[₁₂₃₄₅₆₇₈₉]", token):
        return "other"
    return "none"


def in_scope_series_token(token: str) -> bool:
    """Whether ticket-28 extraction applies to this token."""
    return classify_subscript_token(token) in {"correspondence", "collective"}


def is_positional_slot_token(token: str) -> bool:
    return bool(_POSITIONAL_SLOT_RE.match(token))


def is_identity_subscript_token(token: str) -> bool:
    return bool(_IDENTITY_SUBSCRIPT_RE.match(token))


def is_collective_subscript_token(token: str) -> bool:
    base = token[:-1] if token.endswith("ₓ") else ""
    return len(token) >= 2 and token.endswith("ₓ") and base.isalpha() and base.islower()


def is_correspondence_series_token(token: str) -> bool:
    if is_positional_slot_token(token) or is_identity_subscript_token(token):
        return False
    if is_collective_subscript_token(token):
        return True
    match = _CORRESPONDENCE_INDEX_RE.fullmatch(token)
    if not match:
        return False
    base = match.group(1)
    # Correspondence-series indices attach to concrete (lowercase) segments, not class letters.
    return base.islower()


def find_subscript_tokens(text: str) -> set[str]:
    """Return subscript-bearing tokens appearing in rule field text."""
    return {
        match.group(0) for match in _SUBSCRIPT_TOKEN_RE.finditer(text) if match.group(0)
    }


def find_correspondence_series_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for base, sub in _CORRESPONDENCE_INDEX_RE.findall(text):
        tokens.add(f"{base}{sub}")
    for base in _COLLECTIVE_TOKEN_RE.findall(text):
        tokens.add(f"{base}ₓ")
    return tokens


def section_index_prefixes(section_index: str) -> list[str]:
    parts = [part for part in section_index.split(".") if part]
    return [".".join(parts[:index]) for index in range(len(parts), 0, -1)]


def asca_digit_segment(base: str, subscript_digit: str) -> str:
    """Map Index ``base`` + subscript digit to an ASCA-parseable segment name."""
    ascii_digit = subscript_digit.translate(_SUBSCRIPT_TO_ASCII)
    if base.upper() in _ASCA_GROUPING_LETTERS:
        # ``s₁`` cannot become ``s1`` (ASCA reads ``S`` + reference ``1``).
        return f"f{ascii_digit}"
    return f"{base}{ascii_digit}"


def lookup_series_target(
    section_index: str,
    token: str,
    rows: list[SeriesMapping],
) -> SeriesMapping | None:
    keyed = {(row.section_index, row.token): row for row in rows}
    for prefix in section_index_prefixes(section_index):
        hit = keyed.get((prefix, token))
        if hit is not None:
            return hit
    return keyed.get(("*", token))


def expand_series_tokens_in_field(
    text: str,
    section_index: str,
    rows: list[SeriesMapping],
) -> str:
    """Expand in-scope correspondence-series tokens using hierarchical section lookup."""
    if not text or not rows or not section_index:
        return text
    replacements: list[tuple[str, str]] = []
    for token in find_subscript_tokens(text):
        if not in_scope_series_token(token):
            continue
        hit = lookup_series_target(section_index, token, rows)
        if hit is not None:
            replacements.append((token, hit.asca_target))
    if not replacements:
        return text
    replacements.sort(key=lambda pair: len(pair[0]), reverse=True)
    result = text
    for token, target in replacements:
        result = result.replace(token, target)
    return result


def apply_series_expansions(
    parts: dict[str, Any],
    expansions: dict[str, tuple[str, ...]],
) -> dict[str, Any]:
    """Expand collective subscript tokens in rule fields; ``raw`` unchanged upstream."""
    if not expansions:
        return parts
    result = dict(parts)
    stages = result.get("stages")
    if stages is not None:
        result["stages"] = [
            expand_collectives_in_field(stage, expansions) for stage in stages
        ]
    for key in ("env", "exception"):
        if key in result:
            result[key] = expand_collectives_in_field(result[key], expansions)
    return result


def expand_collectives_in_field(
    text: str,
    expansions: dict[str, tuple[str, ...]],
) -> str:
    """Fan out collective ``Xₓ`` tokens per ``parser_config`` ``series_expansions``."""
    if not text or not expansions:
        return text
    ordered = sorted(expansions.items(), key=lambda pair: len(pair[0]), reverse=True)
    parts: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "{":
            close = text.find("}", index)
            if close == -1:
                parts.append(_expand_collectives_outside_braces(text[index:], ordered))
                break
            inner = text[index + 1 : close]
            parts.append("{" + _expand_collectives_inside_braces(inner, ordered) + "}")
            index = close + 1
        else:
            next_brace = text.find("{", index)
            if next_brace == -1:
                parts.append(_expand_collectives_outside_braces(text[index:], ordered))
                break
            parts.append(
                _expand_collectives_outside_braces(text[index:next_brace], ordered)
            )
            index = next_brace
    return "".join(parts)


def _expand_collectives_inside_braces(
    inner: str,
    ordered: list[tuple[str, tuple[str, ...]]],
) -> str:
    result = inner
    for token, members in ordered:
        if token in result:
            result = result.replace(token, ",".join(members))
    return result


def _expand_collectives_outside_braces(
    segment: str,
    ordered: list[tuple[str, tuple[str, ...]]],
) -> str:
    result = segment
    for token, members in ordered:
        if token in result:
            result = result.replace(token, "{" + ",".join(members) + "}")
    return result


def apply_series_mappings(
    parts: dict[str, str],
    section_index: str,
    rows: list[SeriesMapping],
) -> dict[str, str]:
    """Expand correspondence-series tokens in rule fields; ``raw`` unchanged upstream."""
    if not rows or not section_index:
        return parts
    result = dict(parts)
    stages = result.get("stages")
    if stages is not None:
        result["stages"] = [
            expand_series_tokens_in_field(stage, section_index, rows)
            for stage in stages
        ]
    for key in ("env", "exception"):
        if key in result:
            result[key] = expand_series_tokens_in_field(
                result[key], section_index, rows
            )
    return result


def section_abbreviations_for_index(
    section_index: str,
    rows: list[SeriesMapping],
) -> dict[str, str]:
    """Build section ``abbreviations`` from series rows applicable to ``section_index``."""
    if not rows or not section_index:
        return {}
    prefixes = set(section_index_prefixes(section_index)) | {"*"}
    matching = [
        row
        for row in rows
        if row.section_index in prefixes and in_scope_series_token(row.token)
    ]
    matching.sort(
        key=lambda row: (
            0 if row.section_index == "*" else len(row.section_index.split(".")),
            row.section_index,
            row.token,
        )
    )
    abbrevs: dict[str, str] = {}
    for row in matching:
        abbrevs[row.token] = row.asca_target
    return abbrevs
