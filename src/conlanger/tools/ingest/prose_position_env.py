"""Parse-time normalization for Index prose position phrases in env fields (ticket 107)."""

from __future__ import annotations

import re
from typing import Any

from conlanger.tools.ingest.transforms import _append_rule_comment_parts

_FINAL_SYLLABLE_ENV = "U#"
_FINAL_SYLLABLE_RE = re.compile(
    r"^(?:in\s+)?(?:final\s+syllables?|syllable[- ]finally|syllable[- ]final)\s*$",
    re.IGNORECASE,
)
_NEXT_OR_ADJACENT_TO_SET_RE = re.compile(
    r"^(?:next|adjacent)\s+to\s+(\{[^}]+\})\s*$",
    re.IGNORECASE,
)
_ADJACENT_NASAL_VOWEL_RE = re.compile(
    r"^adjacent\s+to\s+a\s+nasal\s+vowel\s*$",
    re.IGNORECASE,
)
_UNSTRESSED_SYLLABLES_RE = re.compile(r"^unstressed\s+syllables?\s*$", re.IGNORECASE)
_STRESSED_MONOSYLLABLE_RE = re.compile(
    r"^(?:in\s+)?accented\s+or\s+stressed\s+monosyllables?\s*$",
    re.IGNORECASE,
)
_TYPICALLY_NEAR_U_RE = re.compile(r"^typically\s+near\s+\*?u\s*$", re.IGNORECASE)
_BETWEEN_TWO_VOWELS_RE = re.compile(
    r"^between\s+two\s+vowels(?:\s+of\s+unlike\s+nasality)?\s*$",
    re.IGNORECASE,
)
_NOT_UNIVERSAL_RE = re.compile(r"^not\s+universal\??\s*$", re.IGNORECASE)
_MONOSYLLABLE_RE = re.compile(r"^(?:in\s+)?monosyllables?\s*$", re.IGNORECASE)
_TRAILING_POSITION_QUALIFIER_RE = re.compile(
    r"^(?P<env>.+?),\s*in\s+(?P<qual>monosyllables?|polysyllables?|nouns)\s*$",
    re.IGNORECASE,
)


def strip_trailing_position_qualifiers(text: str) -> tuple[str, list[str]]:
    """Peel `, in monosyllables` / `polysyllables` / `nouns` tails from structural envs."""
    if not text:
        return text, []
    stripped = text.strip()
    match = _TRAILING_POSITION_QUALIFIER_RE.match(stripped)
    if not match:
        return text, []
    qualifier = match.group("qual").lower()
    return match.group("env").rstrip(), [f"in {qualifier}"]


def normalize_bare_prose_position_env(
    text: str,
) -> tuple[str, list[str], dict[str, Any]]:
    """Normalize bare Index position prose env phrases for ASCA focus/env encoding."""
    if not text:
        return text, [], {}
    stripped = text.strip()
    flags: dict[str, Any] = {}
    captures: list[str] = []

    if _FINAL_SYLLABLE_RE.match(stripped):
        return _FINAL_SYLLABLE_ENV, [stripped], flags

    match = _NEXT_OR_ADJACENT_TO_SET_RE.match(stripped)
    if match:
        return f"_,{match.group(1)}", [stripped], flags

    if _ADJACENT_NASAL_VOWEL_RE.match(stripped):
        return "_V[+nasal], V[+nasal]_", [stripped], flags

    if _UNSTRESSED_SYLLABLES_RE.match(stripped):
        return "_ %[-stress]", [stripped], flags

    if _STRESSED_MONOSYLLABLE_RE.match(stripped):
        return "#_[+stress]", [stripped], flags

    if _TYPICALLY_NEAR_U_RE.match(stripped):
        return "_,u", [stripped], flags

    if _BETWEEN_TWO_VOWELS_RE.match(stripped):
        return "V_V", [stripped], flags

    if _NOT_UNIVERSAL_RE.match(stripped):
        flags["sporadic"] = True
        return "_", [stripped], flags

    if _MONOSYLLABLE_RE.match(stripped):
        return "#_#", [stripped], flags

    return text, captures, flags


def apply_prose_position_env_conditions(parts: dict[str, Any]) -> dict[str, Any]:
    """Rewrite Index prose position env phrases on ``env`` (``raw`` unchanged)."""
    result: dict[str, Any] = dict(parts)
    env = result.get("env")
    if not env:
        return result

    comment_fragments: list[str] = []
    qualifier_env, qualifier_captures = strip_trailing_position_qualifiers(env)
    if qualifier_captures:
        env = qualifier_env
        comment_fragments.extend(qualifier_captures)

    if result.get("exception"):
        if env != result.get("env"):
            result["env"] = env
            _append_rule_comment_parts(result, comment_fragments)
        return result

    normalized, captures, flags = normalize_bare_prose_position_env(env)
    if normalized != env or captures or flags:
        result["env"] = normalized
        comment_fragments.extend(captures)
        if flags.get("sporadic"):
            result["sporadic"] = True
        _append_rule_comment_parts(result, comment_fragments)
    elif comment_fragments:
        result["env"] = env
        _append_rule_comment_parts(result, comment_fragments)

    return result
