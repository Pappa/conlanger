"""Subscript token classification and parse-time collective expansion."""

from __future__ import annotations

import re
from typing import Any

# Correspondence-series index: concrete segment base + ordinal subscript (not ₀, not ₓ).
_CORRESPONDENCE_INDEX_RE = re.compile(r"(?<![A-Z])([a-zA-Zæøåɑɡɢ]+)([₁₂₃₄₅₆₇₈₉])")
_COLLECTIVE_TOKEN_RE = re.compile(r"(?<![A-Z])([a-zA-Z]+)ₓ")
_POSITIONAL_SLOT_RE = re.compile(r"^[A-Z][₁₂₃₄₅₆₇₈₉]$")
_IDENTITY_SUBSCRIPT_RE = re.compile(r"^[A-Za-z]₀$")
# Any token containing an Index subscript digit/letter (includes compounds like ``eh₂``, ``CV₁``).
_SUBSCRIPT_TOKEN_RE = re.compile(r"[A-Za-zæøåɑɡɢ]*[₀₁₂₃₄₅₆₇₈₉ₓ]+")


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
    return [".".join(parts[:index]) for index in range(1, len(parts) + 1)]


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
