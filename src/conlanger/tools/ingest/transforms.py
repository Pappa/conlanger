"""Field-level ingest transforms for Index → cleaned index rules."""

from __future__ import annotations

from typing import Any

from conlanger.tools.compile.asca.syllable_position import (
    strip_editorial_in_before_syllable_position,
)
from conlanger.tools.ingest.index_models import (
    IndexContext,
    IndexRule,
    join_rule_comment,
)
from conlanger.tools.ingest.transform_fields import (
    MEDIAL_BOUNDARY_EXCEPTION,
    normalize_medial_env_field,
    normalize_stress_conditions,
)
from conlanger.utils.gloss import (
    comment_has_uncertainty_qualifier,
    extract_field_wrapped_quoted_gloss_from_field,
    extract_trailing_gloss_from_field,
    extract_uncertainty_qualifier_from_field,
    field_has_uncertainty_qualifier,
)


def _context_text(ctx: IndexContext | None) -> str | None:
    if ctx is None:
        return None
    return ctx.context


def append_rule_comment_parts(parts: dict[str, Any], fragments: list[str]) -> None:
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
    if rule.comment and comment_has_uncertainty_qualifier(rule.comment):
        rule.sporadic = True
    comment_fragments: list[str] = []
    new_stages: list[str] = []
    for stage in rule.stages:
        value = stage
        if field_has_uncertainty_qualifier(value):
            rule.sporadic = True
        value, captures = extract_uncertainty_qualifier_from_field(value)
        comment_fragments.extend(captures)
        new_stages.append(value)
    rule.stages = new_stages
    for field in IndexRule.context_fields:
        text = _context_text(getattr(rule, field))
        if text is None:
            continue
        if field_has_uncertainty_qualifier(text):
            rule.sporadic = True
        value, captures = extract_uncertainty_qualifier_from_field(text)
        comment_fragments.extend(captures)
        setattr(rule, field, value if value else None)
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
    for field in IndexRule.context_fields:
        original = _context_text(getattr(rule, field))
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
        setattr(rule, field, value if value else None)
    rule.merge_comment(*comment_fragments)
    return rule


def apply_stress_conditions(rule: IndexRule) -> IndexRule:
    """Normalize ``when stressed`` / ``when unstressed`` in env and exception fields."""
    rule = rule.model_copy(deep=True)
    comment_fragments: list[str] = []
    for field in IndexRule.context_fields:
        text = _context_text(getattr(rule, field))
        if text is None:
            continue
        value, captures = normalize_stress_conditions(text)
        setattr(rule, field, value if value else None)
        comment_fragments.extend(captures)
    rule.merge_comment(*comment_fragments)
    return rule


def apply_syllable_position_editorial_strip(rule: IndexRule) -> IndexRule:
    """Normalize mechanical ``in #U`` / ``in U#`` tails on env and exception fields."""
    rule = rule.model_copy(deep=True)
    for field in IndexRule.context_fields:
        text = _context_text(getattr(rule, field))
        if text:
            setattr(rule, field, strip_editorial_in_before_syllable_position(text))
    return rule


def apply_medial_env_conditions(rule: IndexRule) -> IndexRule:
    """Rewrite Index word-internal ``medial`` env prose to ``_`` + boundary exception."""
    rule = rule.model_copy(deep=True)
    if rule.exception is not None:
        return rule
    env = _context_text(rule.env)
    if not env:
        return rule
    normalized, is_medial = normalize_medial_env_field(env)
    if not is_medial:
        return rule
    rule.env = normalized
    rule.exception = MEDIAL_BOUNDARY_EXCEPTION
    return rule


__all__ = [
    "MEDIAL_BOUNDARY_EXCEPTION",
    "append_rule_comment_parts",
    "apply_medial_env_conditions",
    "apply_sporadic_qualifier",
    "apply_stress_conditions",
    "apply_syllable_position_editorial_strip",
    "apply_trailing_glosses",
    "normalize_medial_env_field",
    "normalize_stress_conditions",
]
