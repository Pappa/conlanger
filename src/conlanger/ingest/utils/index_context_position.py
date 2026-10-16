"""Post-split extraction of structured ``IndexContext.position`` (ticket 143)."""

from __future__ import annotations

import re
from typing import Any

from conlanger.ingest.models.index_models import IndexContext, IndexRule, PositionValue
from conlanger.ingest.utils.transform_fields import normalize_medial_env_field

_ADJACENT_TO_SET_RE = re.compile(
    r"^adjacent\s+to\s+(\{[^}]+\})\s*$",
    re.IGNORECASE,
)
_ADJACENT_TO_SINGLE_SEGMENT_RE = re.compile(
    r"^adjacent\s+to\s+(\S+)\s*$",
    re.IGNORECASE,
)
_ADJACENT_TO_SEGMENT_WITH_FEATURE_RE = re.compile(
    r"^adjacent\s+to\s+(\w\[[^]]+\])\s*$",
    re.IGNORECASE,
)
_ADJACENT_TO_PAREN_SEGMENT_RE = re.compile(
    r"^adjacent\s+to\s+(\w?\([^)]+\))\s*$", re.IGNORECASE
)

_NEAR_SET_RE = re.compile(r"^near\s+(\{[^}]+\})\s*$", re.IGNORECASE)
_NEAR_SINGLE_SEGMENT_RE = re.compile(r"^near\s+(\S+)\s*$", re.IGNORECASE)
_NEAR_SEGMENT_WITH_FEATURE_RE = re.compile(
    r"^near\s+(\w\[[^]]+\])\s*$",
    re.IGNORECASE,
)
_NEAR_PAREN_SEGMENT_RE = re.compile(r"^near\s+(\w?\([^)]+\))\s*$", re.IGNORECASE)


def _extract_neighbour_target(stripped: str) -> tuple[str, str] | None:
    for relation, patterns in (
        (
            "adjacent_to",
            (
                _ADJACENT_TO_SET_RE,
                _ADJACENT_TO_SEGMENT_WITH_FEATURE_RE,
                _ADJACENT_TO_PAREN_SEGMENT_RE,
                _ADJACENT_TO_SINGLE_SEGMENT_RE,
            ),
        ),
        (
            "near",
            (
                _NEAR_SET_RE,
                _NEAR_SEGMENT_WITH_FEATURE_RE,
                _NEAR_PAREN_SEGMENT_RE,
                _NEAR_SINGLE_SEGMENT_RE,
            ),
        ),
    ):
        for pattern in patterns:
            match = pattern.match(stripped)
            if match:
                return relation, match.group(1)
    return None


def extract_position_from_context(
    text: str,
) -> tuple[str | None, dict[str, PositionValue]]:
    """Parse neighbour / medial prose from one env or exception ``context`` string."""
    if not text:
        return text, {}
    stripped = text.strip()
    if not stripped:
        return None, {}

    normalized, is_medial = normalize_medial_env_field(stripped)
    if is_medial:
        if normalized == "_":
            return None, {"medial": True}
        return normalized or None, {"medial": True}

    neighbour = _extract_neighbour_target(stripped)
    if neighbour:
        relation, target = neighbour
        return None, {relation: target}

    return text, {}


def apply_position_extraction_to_context(ctx: IndexContext) -> IndexContext | None:
    """Merge extracted ``position`` keys into ``ctx`` and trim ``context``."""
    remainder, extracted = extract_position_from_context(ctx.context or "")
    if not extracted and remainder == (ctx.context or ""):
        return ctx

    position: dict[str, Any] = dict(ctx.position or {})
    position.update(extracted)
    new_context = remainder if remainder else None

    if not new_context and not position and ctx.dialect is None:
        return None
    if not position:
        position = None
    return IndexContext(context=new_context, position=position, dialect=ctx.dialect)


def apply_index_context_position_extraction(rule: IndexRule) -> IndexRule:
    """Extract ``adjacent_to``, ``near``, and ``medial`` onto env / exception contexts."""
    rule = rule.model_copy(deep=True)
    if rule.env is not None:
        rule.env = apply_position_extraction_to_context(rule.env)
    if rule.exception is not None:
        rule.exception = apply_position_extraction_to_context(rule.exception)
    return rule


__all__ = [
    "apply_index_context_position_extraction",
    "apply_position_extraction_to_context",
    "extract_position_from_context",
]
