"""Orchestration entrypoints: run a named ingest pass on an ``IndexRule``."""

from __future__ import annotations

from conlanger.tools.ingest import index_rule_passes
from conlanger.tools.ingest.index_models import IndexRule
from conlanger.tools.ingest.ingest_parse_pass import with_ingest_pass
from conlanger.utils.mappings import FeatureMapping


def apply_sporadic_qualifier(rule: IndexRule) -> IndexRule:
    """Strip uncertainty glosses from rule fields; set ``sporadic: true`` when found."""
    return with_ingest_pass("sporadic", rule)


def apply_trailing_glosses(rule: IndexRule) -> IndexRule:
    """Remove trailing bracket/quote glosses from rule fields; capture ``comment``."""
    return with_ingest_pass("trailing_glosses", rule)


def apply_stress_conditions(rule: IndexRule) -> IndexRule:
    """Normalize ``when stressed`` / ``when unstressed`` in env and exception fields."""
    return with_ingest_pass("stress", rule)


def apply_syllable_position_editorial_strip(rule: IndexRule) -> IndexRule:
    """Normalize mechanical ``in #U`` / ``in U#`` tails on env and exception fields."""
    return with_ingest_pass("syllable_position_editorial", rule)


def apply_medial_env_conditions(rule: IndexRule) -> IndexRule:
    """Rewrite Index word-internal ``medial`` env prose to ``_`` + boundary exception."""
    return with_ingest_pass("medial_env", rule)


def apply_prose_conditional_env_conditions(rule: IndexRule) -> IndexRule:
    """Rewrite Index prose conditional env phrases on ``env`` (``raw`` unchanged)."""
    return with_ingest_pass("prose_conditional_env", rule)


def apply_prose_position_env_conditions(rule: IndexRule) -> IndexRule:
    """Rewrite Index prose position env phrases on ``env`` (``raw`` unchanged)."""
    return with_ingest_pass("prose_position_env", rule)


def apply_double_slash_env_conditions(rule: IndexRule) -> IndexRule:
    """Rewrite Index ``//`` env shorthand and prose exception tails (``raw`` unchanged)."""
    return with_ingest_pass("double_slash_env", rule)


def apply_series_expansions(
    rule: IndexRule,
    expansions: dict[str, tuple[str, ...]],
) -> IndexRule:
    """Expand collective subscript tokens in rule fields; ``raw`` unchanged upstream."""
    if not expansions:
        return rule
    index_rule_passes._pass_series_expansions_data = expansions
    try:
        return with_ingest_pass("series_expansions", rule)
    finally:
        index_rule_passes._pass_series_expansions_data = None


def apply_feature_mappings(
    rule: IndexRule,
    mappings: dict[str, FeatureMapping],
) -> IndexRule:
    """Normalize Index feature matrix names in rule fields; ``raw`` unchanged upstream."""
    if not mappings:
        return rule
    index_rule_passes._pass_feature_mappings_data = mappings
    try:
        return with_ingest_pass("feature_mappings", rule)
    finally:
        index_rule_passes._pass_feature_mappings_data = None


def apply_ipa_mappings(
    rule: IndexRule,
    mappings: dict[str, str],
) -> IndexRule:
    """Normalize Index IPA characters in rule fields; ``raw`` unchanged upstream."""
    if not mappings:
        return rule
    index_rule_passes._pass_ipa_mappings_data = mappings
    try:
        return with_ingest_pass("ipa_mappings", rule)
    finally:
        index_rule_passes._pass_ipa_mappings_data = None
