"""Apply corpus-level mapping helpers to ``IndexRule`` (stages + env/exception)."""

from __future__ import annotations

from conlanger.tools.ingest.index_models import IndexContext, IndexRule
from conlanger.utils.mappings import (
    FeatureMapping,
    normalize_feature_matrices_in_field,
    normalize_ipa_in_field,
)
from conlanger.utils.series import expand_collectives_in_field

_CORPUS_CONTEXT_FIELDS = ("env", "exception")


def apply_series_expansions(
    rule: IndexRule,
    expansions: dict[str, tuple[str, ...]],
) -> IndexRule:
    """Expand collective subscript tokens on stages and env/exception context."""
    if not expansions:
        return rule
    rule = rule.model_copy(deep=True)
    rule.stages = [
        expand_collectives_in_field(stage, expansions) for stage in rule.stages
    ]
    for field in _CORPUS_CONTEXT_FIELDS:
        ctx: IndexContext | None = getattr(rule, field)
        if ctx is not None and ctx.context:
            setattr(
                rule,
                field,
                expand_collectives_in_field(ctx.context, expansions),
            )
    return rule


def apply_feature_mappings(
    rule: IndexRule,
    mappings: dict[str, FeatureMapping],
) -> IndexRule:
    """Normalize feature matrices on stages and env/exception context."""
    if not mappings:
        return rule
    rule = rule.model_copy(deep=True)
    rule.stages = [
        normalize_feature_matrices_in_field(stage, mappings) for stage in rule.stages
    ]
    for field in _CORPUS_CONTEXT_FIELDS:
        ctx: IndexContext | None = getattr(rule, field)
        if ctx is not None and ctx.context:
            setattr(
                rule,
                field,
                normalize_feature_matrices_in_field(ctx.context, mappings),
            )
    return rule


def apply_ipa_mappings(rule: IndexRule, mappings: dict[str, str]) -> IndexRule:
    """Normalize IPA on stages and env/exception context."""
    if not mappings:
        return rule
    rule = rule.model_copy(deep=True)
    rule.stages = [normalize_ipa_in_field(stage, mappings) for stage in rule.stages]
    for field in _CORPUS_CONTEXT_FIELDS:
        ctx: IndexContext | None = getattr(rule, field)
        if ctx is not None and ctx.context:
            setattr(rule, field, normalize_ipa_in_field(ctx.context, mappings))
    return rule
