"""Ingest parse-pass mutations run from ``IndexRule`` validation (see ``ingest_parse_pass``)."""

from __future__ import annotations

from typing import Any

from conlanger.tools.compile.asca.syllable_position import (
    strip_editorial_in_before_syllable_position,
)
from conlanger.tools.ingest.double_slash_env import (
    normalize_prose_env_head,
    normalize_prose_exception_or_env_tail,
    split_embedded_double_slash,
)
from conlanger.tools.ingest.index_models import IndexContext, IndexRule
from conlanger.tools.ingest.ingest_parse_context import current_ingest_parse_pass
from conlanger.tools.ingest.prose_conditional_env import (
    _attach_bare_matrix_to_input_stage,
    normalize_prose_conditional_env_field,
)
from conlanger.tools.ingest.prose_position_env import (
    normalize_bare_prose_position_env,
    strip_trailing_position_qualifiers,
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
from conlanger.utils.mappings import (
    normalize_feature_matrices_in_field,
    normalize_ipa_in_field,
)
from conlanger.utils.series import expand_collectives_in_field

_CONTEXT_FIELDS = ("env", "exception")


def _context_text(ctx: IndexContext | None) -> str | None:
    if ctx is None:
        return None
    return ctx.context


def run_ingest_parse_pass(rule: IndexRule) -> None:
    name = current_ingest_parse_pass()
    if name is None:
        return
    handlers: dict[str, Any] = {
        "series_expansions": _pass_series_expansions,
        "sporadic": _pass_sporadic,
        "trailing_glosses": _pass_trailing_glosses,
        "stress": _pass_stress,
        "prose_conditional_env": _pass_prose_conditional_env,
        "medial_env": _pass_medial_env,
        "prose_position_env": _pass_prose_position_env,
        "double_slash_env": _pass_double_slash_env,
        "syllable_position_editorial": _pass_syllable_position_editorial,
        "feature_mappings": _pass_feature_mappings,
        "ipa_mappings": _pass_ipa_mappings,
        "dialects": _pass_dialects,
    }
    handler = handlers.get(name)
    if handler is not None:
        handler(rule)


def _pass_prose_position_env(rule: IndexRule) -> None:
    env = _context_text(rule.env)
    if not env:
        return

    comment_fragments: list[str] = []
    qualifier_env, qualifier_captures = strip_trailing_position_qualifiers(env)
    if qualifier_captures:
        env = qualifier_env
        comment_fragments.extend(qualifier_captures)

    if rule.exception is not None:
        if env != _context_text(rule.env):
            rule.env = env
            rule.merge_comment(*comment_fragments)
        return

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


def _pass_stress(rule: IndexRule) -> None:
    comment_fragments: list[str] = []
    for field in _CONTEXT_FIELDS:
        text = _context_text(getattr(rule, field))
        if text is None:
            continue
        value, captures = normalize_stress_conditions(text)
        setattr(rule, field, value if value else None)
        comment_fragments.extend(captures)
    rule.merge_comment(*comment_fragments)


def _pass_medial_env(rule: IndexRule) -> None:
    if rule.exception is not None:
        return
    env = _context_text(rule.env)
    if not env:
        return
    normalized, is_medial = normalize_medial_env_field(env)
    if not is_medial:
        return
    rule.env = normalized
    rule.exception = MEDIAL_BOUNDARY_EXCEPTION


def _pass_double_slash_env(rule: IndexRule) -> None:
    comment_fragments: list[str] = []
    flags: dict[str, Any] = {}

    env = _context_text(rule.env)
    exception = _context_text(rule.exception)

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

        rule.env = env if env else None

    if exception:
        original_exception = exception
        value, uncertainty_captures = extract_uncertainty_qualifier_from_field(
            exception
        )
        if uncertainty_captures:
            comment_fragments.extend(uncertainty_captures)
            flags["sporadic"] = True

        normalized, tail_captures, tail_flags = normalize_prose_exception_or_env_tail(
            value
        )
        if (
            normalized != original_exception
            or tail_captures
            or tail_flags
            or value != original_exception
        ):
            rule.exception = normalized if normalized else None
            comment_fragments.extend(tail_captures)
            flags.update(tail_flags)

    rule.merge_comment(*comment_fragments)
    if flags.get("sporadic"):
        rule.sporadic = True


def _pass_prose_conditional_env(rule: IndexRule) -> None:
    env = _context_text(rule.env)
    if env:
        normalized, captures, flags, input_matrix = (
            normalize_prose_conditional_env_field(env)
        )
        comment_fragments = list(captures)
        if normalized != env or comment_fragments or flags or input_matrix:
            rule.env = normalized if normalized else None
            if input_matrix and rule.stages:
                merged = _attach_bare_matrix_to_input_stage(rule.stages, input_matrix)
                if merged is not None:
                    rule.stages = merged
            if flags.get("sporadic"):
                rule.sporadic = True
            rule.merge_comment(*comment_fragments)

    exception = _context_text(rule.exception)
    if exception:
        exc_norm, exc_caps, exc_flags, _ = normalize_prose_conditional_env_field(
            exception
        )
        if exc_norm != exception or exc_caps or exc_flags:
            rule.exception = exc_norm if exc_norm else None
            if exc_flags.get("sporadic"):
                rule.sporadic = True
            rule.merge_comment(*exc_caps)


def _pass_sporadic(rule: IndexRule) -> None:
    sporadic = bool(rule.sporadic)
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
    for field in _CONTEXT_FIELDS:
        text = _context_text(getattr(rule, field))
        if text is None:
            continue
        if field_has_uncertainty_qualifier(text):
            sporadic = True
        value, captures = extract_uncertainty_qualifier_from_field(text)
        comment_fragments.extend(captures)
        setattr(rule, field, value if value else None)
    if sporadic:
        rule.sporadic = True
    rule.merge_comment(*comment_fragments)


def _pass_trailing_glosses(rule: IndexRule) -> None:
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
    for field in _CONTEXT_FIELDS:
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


def _pass_syllable_position_editorial(rule: IndexRule) -> None:
    for field in _CONTEXT_FIELDS:
        text = _context_text(getattr(rule, field))
        if text:
            setattr(rule, field, strip_editorial_in_before_syllable_position(text))


def _pass_dialects(rule: IndexRule) -> None:
    if rule.env is not None:
        rule.env = rule.env.with_dialects_extracted()
    if rule.exception is not None:
        rule.exception = rule.exception.with_dialects_extracted()


# Set by apply_* wrappers before revalidation
_pass_series_expansions_data: dict[str, tuple[str, ...]] | None = None
_pass_feature_mappings_data: dict | None = None
_pass_ipa_mappings_data: dict[str, str] | None = None


def _pass_series_expansions(rule: IndexRule) -> None:
    expansions = _pass_series_expansions_data
    if not expansions:
        return
    rule.stages = [
        expand_collectives_in_field(stage, expansions) for stage in rule.stages
    ]
    for field in _CONTEXT_FIELDS:
        text = _context_text(getattr(rule, field))
        if text:
            setattr(
                rule,
                field,
                expand_collectives_in_field(text, expansions),
            )


def _pass_feature_mappings(rule: IndexRule) -> None:
    mappings = _pass_feature_mappings_data
    if not mappings:
        return
    rule.stages = [
        normalize_feature_matrices_in_field(stage, mappings) for stage in rule.stages
    ]
    for field in _CONTEXT_FIELDS:
        text = _context_text(getattr(rule, field))
        if text:
            setattr(
                rule,
                field,
                normalize_feature_matrices_in_field(text, mappings),
            )


def _pass_ipa_mappings(rule: IndexRule) -> None:
    mappings = _pass_ipa_mappings_data
    if not mappings:
        return
    rule.stages = [normalize_ipa_in_field(stage, mappings) for stage in rule.stages]
    for field in _CONTEXT_FIELDS:
        text = _context_text(getattr(rule, field))
        if text:
            setattr(rule, field, normalize_ipa_in_field(text, mappings))
