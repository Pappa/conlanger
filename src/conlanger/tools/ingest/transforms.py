"""Field-level ingest transforms for Index → cleaned index rules."""

from __future__ import annotations

from typing import Any

from conlanger.tools.ingest.index_models import join_rule_comment
from conlanger.tools.ingest.ingest_apply import (
    apply_medial_env_conditions,
    apply_sporadic_qualifier,
    apply_stress_conditions,
    apply_syllable_position_editorial_strip,
    apply_trailing_glosses,
)
from conlanger.tools.ingest.transform_fields import (
    MEDIAL_BOUNDARY_EXCEPTION,
    normalize_medial_env_field,
    normalize_stress_conditions,
)

__all__ = [
    "MEDIAL_BOUNDARY_EXCEPTION",
    "apply_medial_env_conditions",
    "apply_sporadic_qualifier",
    "apply_stress_conditions",
    "apply_syllable_position_editorial_strip",
    "apply_trailing_glosses",
    "normalize_medial_env_field",
    "normalize_stress_conditions",
]


def _append_rule_comment_parts(parts: dict[str, Any], fragments: list[str]) -> None:
    """Merge newly captured prose into optional ``comment`` on serialized rule dicts."""
    addition = join_rule_comment(*fragments)
    if not addition:
        return
    existing = parts.get("comment")
    merged = join_rule_comment(existing, addition)
    if merged:
        parts["comment"] = merged
