"""Field-level ingest transforms for Index → cleaned corpus rules."""

from __future__ import annotations

import re
from typing import Any

from conlanger.utils.gloss import (
    extract_field_wrapped_quoted_gloss_from_field,
    extract_trailing_gloss_from_field,
    extract_uncertainty_qualifier_from_field,
    field_has_uncertainty_qualifier,
)

_CORPUS_CONTEXT_FIELD_KEYS = ("env", "exception")


def join_rule_comment(*fragments: str | None) -> str | None:
    """Join captured prose fragments into one ``comment`` string."""
    parts = [
        fragment.strip() for fragment in fragments if fragment and fragment.strip()
    ]
    if not parts:
        return None
    return "; ".join(parts)


def split_field_semicolon_comment(text: str) -> tuple[str, str | None]:
    """Treat the first ``;`` and following text as ``comment`` prose in one field."""
    return split_line_semicolon_comment(text)


def split_line_semicolon_comment(text: str) -> tuple[str, str | None]:
    """Peel the first ``;`` on a working rule line into remainder and rule-comment tail."""
    if not text or ";" not in text:
        return text, None
    head, _semicolon, tail = text.partition(";")
    head = head.rstrip()
    comment = tail.strip()
    return head, comment or None


def apply_semicolon_field_comments(parts: dict[str, str]) -> dict[str, Any]:
    """Strip semicolon tails from ``env`` and ``exception``; first comment pass."""
    result: dict[str, Any] = dict(parts)
    fragments: list[str] = []
    for key in ("env", "exception"):
        if key not in result:
            continue
        value, comment = split_field_semicolon_comment(result[key])
        result[key] = value
        if comment:
            fragments.append(comment)
    _append_rule_comment_parts(result, fragments)
    return result


def _append_rule_comment_parts(parts: dict[str, Any], fragments: list[str]) -> None:
    """Merge newly captured prose into optional ``comment`` on rule parts."""
    addition = join_rule_comment(*fragments)
    if not addition:
        return
    existing = parts.get("comment")
    merged = join_rule_comment(existing, addition)
    if merged:
        parts["comment"] = merged


def apply_sporadic_qualifier(parts: dict[str, str]) -> dict[str, Any]:
    """Strip uncertainty glosses from rule fields; set ``sporadic: true`` when found."""
    sporadic = False
    cleaned: dict[str, Any] = {}
    if "comment" in parts:
        cleaned["comment"] = parts["comment"]
    comment_fragments: list[str] = []
    stages = parts.get("stages")
    if stages is not None:
        new_stages: list[str] = []
        for stage in stages:
            value = stage
            if field_has_uncertainty_qualifier(value):
                sporadic = True
            value, captures = extract_uncertainty_qualifier_from_field(value)
            comment_fragments.extend(captures)
            new_stages.append(value)
        cleaned["stages"] = new_stages
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        if key not in parts:
            continue
        value = parts[key]
        if field_has_uncertainty_qualifier(value):
            sporadic = True
        value, captures = extract_uncertainty_qualifier_from_field(value)
        comment_fragments.extend(captures)
        if value:
            cleaned[key] = value
    result: dict[str, Any] = cleaned
    if sporadic:
        result["sporadic"] = True
    _append_rule_comment_parts(result, comment_fragments)
    return result


def apply_trailing_glosses(parts: dict[str, str]) -> dict[str, Any]:
    """Remove trailing bracket/quote glosses from rule fields; capture ``comment``."""
    cleaned: dict[str, Any] = {}
    if "comment" in parts:
        cleaned["comment"] = parts["comment"]
    comment_fragments: list[str] = []
    stages = parts.get("stages")
    if stages is not None:
        new_stages: list[str] = []
        for original in stages:
            wrapped_cleaned, wrapped_caps = (
                extract_field_wrapped_quoted_gloss_from_field(original)
            )
            if wrapped_caps:
                value = wrapped_cleaned
                comment_fragments.extend(wrapped_caps)
            else:
                value, captures = extract_trailing_gloss_from_field(original)
                comment_fragments.extend(captures)
                if not value:
                    value = original
            new_stages.append(value)
        cleaned["stages"] = new_stages
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        if key not in parts:
            continue
        original = parts[key]
        wrapped_cleaned, wrapped_caps = extract_field_wrapped_quoted_gloss_from_field(
            original
        )
        if wrapped_caps:
            value = wrapped_cleaned
            comment_fragments.extend(wrapped_caps)
        else:
            value, captures = extract_trailing_gloss_from_field(
                original, include_unclosed_paren=False
            )
            comment_fragments.extend(captures)
        if value:
            cleaned[key] = value
    _append_rule_comment_parts(cleaned, comment_fragments)
    return cleaned


_STRESS_CONDITION_RE = re.compile(r"when (?:un)?stressed\b", re.IGNORECASE)
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


def normalize_stress_conditions(text: str) -> tuple[str, list[str]]:
    """Normalize Index stress env prose for ASCA; capture removed trailing prose."""
    captures: list[str] = []
    if not text or not _STRESS_CONDITION_RE.search(text):
        return text, captures
    text = _COMMA_BEFORE_STRESS_RE.sub(" ", text)
    if "#" in text:
        match = _TRAILING_STRESS_AFTER_HASH_RE.search(text)
        if match:
            captures.append(match.group(0).strip())
            text = _TRAILING_STRESS_AFTER_HASH_RE.sub("", text).rstrip()
    elif re.match(r"when (?:un)?stressed\b", text, re.IGNORECASE):
        text = f"_ {text}"
    elif "_" not in text:
        match = _PROSE_BEFORE_STRESS_RE.match(text)
        if match:
            text = f"_ {match.group(1)}"
    return text.strip(), captures


def apply_stress_conditions(parts: dict[str, str]) -> dict[str, Any]:
    """Normalize ``when stressed`` / ``when unstressed`` in env and exception fields."""
    result: dict[str, Any] = dict(parts)
    comment_fragments: list[str] = []
    for key in ("env", "exception"):
        if key in result:
            value, captures = normalize_stress_conditions(result[key])
            result[key] = value
            comment_fragments.extend(captures)
    _append_rule_comment_parts(result, comment_fragments)
    return result


MEDIAL_BOUNDARY_EXCEPTION = ":{#_, _#}:"
_BARE_MEDIAL_ENV_RE = re.compile(r"^\s*medial(?:ly)?\s*,?\s*$", re.IGNORECASE)
_BARE_WHEN_MEDIAL_ENV_RE = re.compile(r"^\s*when\s+medial(?:ly)?\s*$", re.IGNORECASE)
_WHEN_MEDIAL_SUFFIX_RE = re.compile(r"(?:,\s*)?when\s+medial(?:ly)?\s*$", re.IGNORECASE)


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


def apply_medial_env_conditions(parts: dict[str, Any]) -> dict[str, Any]:
    """Rewrite Index word-internal ``medial`` env prose to ``_`` + boundary exception."""
    result: dict[str, Any] = dict(parts)
    if result.get("exception"):
        return result
    env = result.get("env")
    if not env:
        return result
    normalized, is_medial = normalize_medial_env_field(env)
    if not is_medial:
        return result
    result["env"] = normalized
    result["exception"] = MEDIAL_BOUNDARY_EXCEPTION
    return result
