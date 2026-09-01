"""Parse-time normalization for Index ``//`` env shorthand and prose exceptions (ticket 108)."""

from __future__ import annotations

import re
from typing import Any

from conlanger.tools.ingest.prose_position_env import normalize_bare_prose_position_env
from conlanger.tools.ingest.transforms import (
    _append_rule_comment_parts,
    normalize_medial_env_field,
)
from conlanger.utils.gloss import extract_uncertainty_qualifier_from_field

_DOUBLE_SLASH_SEP = " // "

_ADJACENT_ANOTHER_CONSONANT_RE = re.compile(
    r"^adjacent\s+to\s+another\s+consonant\s*$",
    re.IGNORECASE,
)
_ADJACENT_TO_SINGLE_RE = re.compile(
    r"^(?:next|adjacent)\s+to\s+([^{}\s,]+)\s*$",
    re.IGNORECASE,
)
_ONSET_OF_STRESS_RE = re.compile(
    r"^in\s+onset\s+of\s+(%|U)\[\+stress\]\s*$",
    re.IGNORECASE,
)
_BARE_ONSET_OF_STRESS_RE = re.compile(
    r"^onset\s+of\s+(%|U)\[\+stress\]\s*$",
    re.IGNORECASE,
)
_BEFORE_IDENTICAL_VOWEL_RE = re.compile(
    r"^before\s+an?\s+identical\s+vowel\s*$",
    re.IGNORECASE,
)
_DIALECT_NAME_RE = re.compile(r"^[A-Z][a-zA-Z]+$")
_TYPICALLY_SUFFIX_RE = re.compile(r",\s*typically\s*$", re.IGNORECASE)
_ODD_SYLLABLES_RE = re.compile(r"^(?:in\s+)?odd\s+syllables?\s*$", re.IGNORECASE)
_MAYBE_ENV_RE = re.compile(r"^maybe\??\s*$", re.IGNORECASE)
_VOID_ENV_RE = re.compile(r"^∅$")
_BARE_PERCENT_FEATURE_RE = re.compile(r"^%(\[[^\]]+\]|:[^\s,]+)$")
_BARE_U_FEATURE_RE = re.compile(r"^U(\[[^\]]+\]|:[^\s,]+)$")
_BROKEN_EXCEPTION_TAIL_RE = re.compile(
    r"^(_[^,]+),\s*short\s+only\)\s*$",
    re.IGNORECASE,
)
_COMPLEX_PROSE_EXCEPTION_RE = re.compile(
    r"^#% with the following",
    re.IGNORECASE,
)
_VOICE_EARLIER_RE = re.compile(
    r"^O\[\+voic",
    re.IGNORECASE,
)
_PENULT_RE = re.compile(r"^penult\s*$", re.IGNORECASE)


def split_embedded_double_slash(text: str) -> tuple[str, str | None]:
    """Split ``env`` text on Index `` // `` into env head and optional tail."""
    if not text or _DOUBLE_SLASH_SEP not in text:
        return text, None
    head, tail = text.split(_DOUBLE_SLASH_SEP, 1)
    return head.rstrip(), tail.strip() or None


def normalize_prose_exception_or_env_tail(
    text: str,
) -> tuple[str, list[str], dict[str, Any]]:
    """Normalize prose ``//`` exception tails and bare exception-only rules."""
    if not text:
        return text, [], {}
    stripped = text.strip()
    flags: dict[str, Any] = {}
    captures: list[str] = []

    if _ADJACENT_ANOTHER_CONSONANT_RE.match(stripped):
        return "C_,_C", [stripped], flags

    match = _ADJACENT_TO_SINGLE_RE.match(stripped)
    if match:
        return f"_,{match.group(1)}", [stripped], flags

    normalized, pos_captures, pos_flags = normalize_bare_prose_position_env(stripped)
    if normalized != stripped or pos_captures or pos_flags:
        captures.extend(pos_captures)
        flags.update(pos_flags)
        return normalized, captures, flags

    match = _ONSET_OF_STRESS_RE.match(stripped)
    if match:
        return f"#_{match.group(1)}[+stress]", [stripped], flags
    match = _BARE_ONSET_OF_STRESS_RE.match(stripped)
    if match:
        return f"#_{match.group(1)}[+stress]", [stripped], flags

    if _BEFORE_IDENTICAL_VOWEL_RE.match(stripped):
        return "V_V", [stripped], flags

    if _PENULT_RE.match(stripped):
        return "%_", [stripped], flags

    if _DIALECT_NAME_RE.match(stripped):
        return "", [stripped], flags

    if _COMPLEX_PROSE_EXCEPTION_RE.match(stripped) or _VOICE_EARLIER_RE.match(stripped):
        return text, [stripped], flags

    match = _BROKEN_EXCEPTION_TAIL_RE.match(stripped)
    if match:
        captures.append("short only")
        return match.group(1), captures, flags

    match = _BARE_PERCENT_FEATURE_RE.match(stripped) or _BARE_U_FEATURE_RE.match(
        stripped
    )
    if match:
        prefix = stripped[0]
        return f"_ {prefix}{match.group(1)}", [stripped], flags

    return text, captures, flags


def normalize_prose_env_head(
    text: str,
) -> tuple[str, list[str], dict[str, Any]]:
    """Normalize prose env heads that block ASCA before ``//`` exception tails."""
    if not text:
        return text, [], {}
    stripped = text.strip()
    flags: dict[str, Any] = {}
    captures: list[str] = []

    match = _TYPICALLY_SUFFIX_RE.search(stripped)
    if match:
        captures.append("typically")
        stripped = stripped[: match.start()].rstrip()

    normalized, is_medial = normalize_medial_env_field(stripped)
    if is_medial:
        captures.append(stripped)
        stripped = normalized

    if _MAYBE_ENV_RE.match(stripped):
        flags["sporadic"] = True
        return "_", ["maybe"], flags

    if _VOID_ENV_RE.match(stripped):
        return "", [], flags

    if _ODD_SYLLABLES_RE.match(stripped):
        return "_", [stripped], flags

    normalized, pos_captures, pos_flags = normalize_bare_prose_position_env(stripped)
    if normalized != stripped or pos_captures or pos_flags:
        captures.extend(pos_captures)
        flags.update(pos_flags)
        return normalized, captures, flags

    match = _BARE_PERCENT_FEATURE_RE.match(stripped) or _BARE_U_FEATURE_RE.match(
        stripped
    )
    if match:
        prefix = stripped[0]
        return f"_ {prefix}{match.group(1)}", [stripped], flags

    return stripped, captures, flags


def apply_double_slash_env_conditions(parts: dict[str, Any]) -> dict[str, Any]:
    """Rewrite Index ``//`` env shorthand and prose exception tails (``raw`` unchanged)."""
    result: dict[str, Any] = dict(parts)
    comment_fragments: list[str] = []
    flags: dict[str, Any] = {}

    env = result.get("env")
    exception = result.get("exception")

    if env:
        head, embedded_tail = split_embedded_double_slash(env)
        if embedded_tail:
            env = head
            if exception:
                comment_fragments.append(embedded_tail)
            else:
                exception = embedded_tail

        normalized_head, head_captures, head_flags = normalize_prose_env_head(env)
        if normalized_head != env or head_captures or head_flags:
            env = normalized_head
            comment_fragments.extend(head_captures)
            flags.update(head_flags)
        elif embedded_tail:
            env = head

        if env:
            result["env"] = env
        elif "env" in result:
            del result["env"]

    if exception:
        original_exception = exception
        value, uncertainty_captures = extract_uncertainty_qualifier_from_field(
            exception
        )
        if uncertainty_captures:
            comment_fragments.extend(uncertainty_captures)
            flags["sporadic"] = True
        if flags.get("sporadic") and value.endswith("?"):
            value = value[:-1].rstrip()
        normalized, tail_captures, tail_flags = normalize_prose_exception_or_env_tail(
            value
        )
        if (
            normalized != original_exception
            or tail_captures
            or tail_flags
            or value != original_exception
        ):
            if normalized:
                result["exception"] = normalized
            else:
                del result["exception"]
            comment_fragments.extend(tail_captures)
            flags.update(tail_flags)

    if comment_fragments:
        _append_rule_comment_parts(result, comment_fragments)
    if flags.get("sporadic"):
        result["sporadic"] = True

    return result
