"""Field-level ingest transforms for Index → cleaned index rules."""

from __future__ import annotations

import re
from typing import Any

from conlanger.tools.compile.asca.syllable_position import (
    strip_editorial_in_before_syllable_position,
)
from conlanger.tools.ingest.index_models import IndexRule, join_rule_comment
from conlanger.utils.gloss import (
    comment_has_uncertainty_qualifier,
    extract_field_wrapped_quoted_gloss_from_field,
    extract_trailing_gloss_from_field,
    extract_uncertainty_qualifier_from_field,
    field_has_uncertainty_qualifier,
)

_CORPUS_CONTEXT_FIELD_KEYS = ("env", "exception")


def _append_rule_comment_parts(parts: dict[str, Any], fragments: list[str]) -> None:
    """Merge newly captured prose into optional ``comment`` on serialized rule dicts."""
    addition = join_rule_comment(*fragments)
    if not addition:
        return
    existing = parts.get("comment")
    merged = join_rule_comment(existing, addition)
    if merged:
        parts["comment"] = merged


def apply_sporadic_qualifier(rule: IndexRule) -> IndexRule:
    """Strip uncertainty glosses from rule fields; set ``sporadic: true`` when found."""
    rule = rule.model_copy(deep=True)
    sporadic = False
    if rule.comment and comment_has_uncertainty_qualifier(rule.comment):
        sporadic = True
    comment_fragments: list[str] = []
    new_stages: list[str] = []
    for stage in rule.stages:
        value = stage
        if field_has_uncertainty_qualifier(value):
            sporadic = True
        value, captures = extract_uncertainty_qualifier_from_field(value)
        comment_fragments.extend(captures)
        new_stages.append(value)
    rule.stages = new_stages
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        text = getattr(rule, f"{key}_context")()
        if text is None:
            continue
        if field_has_uncertainty_qualifier(text):
            sporadic = True
        value, captures = extract_uncertainty_qualifier_from_field(text)
        comment_fragments.extend(captures)
        if value:
            getattr(rule, f"set_{key}_context")(value)
        else:
            setattr(rule, key, None)
    if sporadic:
        rule.mark_sporadic()
    rule.merge_comment(*comment_fragments)
    return rule


def apply_trailing_glosses(rule: IndexRule) -> IndexRule:
    """Remove trailing bracket/quote glosses from rule fields; capture ``comment``."""
    rule = rule.model_copy(deep=True)
    comment_fragments: list[str] = []
    new_stages: list[str] = []
    for original in rule.stages:
        wrapped_cleaned, wrapped_caps = extract_field_wrapped_quoted_gloss_from_field(
            original
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
    rule.stages = new_stages
    for key in _CORPUS_CONTEXT_FIELD_KEYS:
        original = getattr(rule, f"{key}_context")()
        if original is None:
            continue
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
            getattr(rule, f"set_{key}_context")(value)
        else:
            setattr(rule, key, None)
    rule.merge_comment(*comment_fragments)
    return rule


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


def apply_stress_conditions(rule: IndexRule) -> IndexRule:
    """Normalize ``when stressed`` / ``when unstressed`` in env and exception fields."""
    rule = rule.model_copy(deep=True)
    comment_fragments: list[str] = []
    for key in ("env", "exception"):
        text = getattr(rule, f"{key}_context")()
        if text is None:
            continue
        value, captures = normalize_stress_conditions(text)
        getattr(rule, f"set_{key}_context")(value if value else None)
        comment_fragments.extend(captures)
    rule.merge_comment(*comment_fragments)
    return rule


MEDIAL_BOUNDARY_EXCEPTION = "#_, _#"
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


def apply_syllable_position_editorial_strip(rule: IndexRule) -> IndexRule:
    """Normalize mechanical ``in #U`` / ``in U#`` tails on env and exception fields."""
    rule = rule.model_copy(deep=True)
    rule.map_env_and_exception_context(strip_editorial_in_before_syllable_position)
    return rule


def apply_medial_env_conditions(rule: IndexRule) -> IndexRule:
    """Rewrite Index word-internal ``medial`` env prose to ``_`` + boundary exception."""
    rule = rule.model_copy(deep=True)
    if rule.exception_context() is not None:
        return rule
    env = rule.env_context()
    if not env:
        return rule
    normalized, is_medial = normalize_medial_env_field(env)
    if not is_medial:
        return rule
    rule.set_env_context(normalized)
    rule.set_exception_context(MEDIAL_BOUNDARY_EXCEPTION)
    return rule
