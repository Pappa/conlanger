"""Parse-time normalization for Index prose position phrases in env fields (ticket 107)."""

from __future__ import annotations

import re
from typing import Any

from conlanger.ingest.models.index_models import IndexRule

_FINAL_SYLLABLE_ENV = "U#"
_FINAL_SYLLABLE_RE = re.compile(
    r"^(?:in\s+)?(?:final\s+syllables?|syllable[- ]finally|syllable[- ]final)\s*$",
    re.IGNORECASE,
)
_UNSTRESSED_SYLLABLES_RE = re.compile(r"^unstressed\s+syllables?\s*$", re.IGNORECASE)
_STRESSED_MONOSYLLABLE_RE = re.compile(
    r"^(?:in\s+)?accented\s+or\s+stressed\s+monosyllables?\s*$",
    re.IGNORECASE,
)
_BETWEEN_TWO_VOWELS_RE = re.compile(
    r"^between\s+two\s+vowels(?:\s+of\s+unlike\s+nasality)?\s*$",  # TODO: this is not correct
    re.IGNORECASE,
)
_NOT_UNIVERSAL_RE = re.compile(r"^\(?not\s+universal\??\)?\s*$", re.IGNORECASE)


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

    if _UNSTRESSED_SYLLABLES_RE.match(stripped):
        # return "_ %[-stress]", [stripped], flags  # TODO: this is not correct
        return "%[-stress]", [stripped], flags  # TODO: this is not correct

    if _STRESSED_MONOSYLLABLE_RE.match(stripped):
        return "#_[+stress]", [stripped], flags  # TODO: this is not correct

    if _BETWEEN_TWO_VOWELS_RE.match(stripped):
        return "V_V", [stripped], flags

    if _NOT_UNIVERSAL_RE.match(stripped):
        flags["sporadic"] = True
        return "_", [stripped], flags

    return text, captures, flags


def apply_prose_position_env_conditions(rule: IndexRule) -> IndexRule:
    """Normalize bare Index position prose in ``env`` (ticket 107)."""
    env = rule.env.context if rule.env else None
    if not env:
        return rule

    comment_fragments: list[str] = []

    if rule.exception is not None:
        return rule

    normalized, captures, flags = normalize_bare_prose_position_env(env)
    if normalized != env or captures or flags:
        rule.env = normalized
        comment_fragments.extend(captures)
        if flags.get("sporadic"):
            rule.sporadic = True
        rule.merge_comment(*comment_fragments)
    elif comment_fragments:
        rule.env = env
        rule.merge_comment(*comment_fragments)
    return rule
