"""Apply corpus-level mapping helpers to ``IndexRule`` (stages + env/exception)."""

from __future__ import annotations

from conlanger.ingest.models.index_models import IndexRule
from conlanger.ingest.models.mappings import (
    FeatureMapping,
    normalize_feature_matrices_in_field,
    normalize_ipa_in_field,
)
from conlanger.utils.series import expand_collectives_in_field


def apply_series_expansions(
    rule: IndexRule,
    series_expansions: dict[str, tuple[str, ...]],
) -> IndexRule:
    """Expand collective subscript tokens on stages and env/exception context."""
    if not series_expansions:
        return rule
    expansions = list(series_expansions.items())
    rule.stages = [
        expand_collectives_in_field(stage, expansions) for stage in rule.stages
    ]
    for ctx in rule.contexts:
        if ctx.context:
            ctx.context = expand_collectives_in_field(ctx.context, expansions)
    return rule


def apply_feature_mappings(
    rule: IndexRule,
    mappings: dict[str, FeatureMapping],
) -> IndexRule:
    """Normalize feature matrices on stages and env/exception context."""
    if not mappings:
        return rule
    rule.stages = [
        normalize_feature_matrices_in_field(stage, mappings) for stage in rule.stages
    ]
    for ctx in rule.contexts:
        if ctx.context:
            ctx.context = normalize_feature_matrices_in_field(ctx.context, mappings)
    return rule


def apply_ipa_mappings(rule: IndexRule, mappings: dict[str, str]) -> IndexRule:
    """Normalize IPA on stages and env/exception context."""
    if not mappings:
        return rule
    rule.stages = [normalize_ipa_in_field(stage, mappings) for stage in rule.stages]
    for ctx in rule.contexts:
        if ctx.context:
            ctx.context = normalize_ipa_in_field(ctx.context, mappings)
    return rule
