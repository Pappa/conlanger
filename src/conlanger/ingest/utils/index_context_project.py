"""Applier-neutral ``IndexContext`` position projection for parse-time policies."""

from __future__ import annotations

from conlanger.ingest.models.index_models import IndexContext, PositionValue

_DEFAULT_POSITION_TEMPLATES: dict[str, str] = {
    "adjacent_to": "{v}_, _{v}",
    "near": "{v}_, _{v}",
    "in": "in {v}",
}


def _position_target_value(value: PositionValue) -> str | None:
    if isinstance(value, list):
        if not value:
            return None
        value = value[0]
    if isinstance(value, str) and value:
        return value
    return None


def _project_position_relation(
    ctx: IndexContext,
    relation: str,
    templates: dict[str, str],
) -> str | None:
    if not ctx.position:
        return None
    target = _position_target_value(ctx.position.get(relation))
    template = templates.get(relation)
    if target is None or template is None:
        return None
    return template.format(v=target)


def project_index_context(
    ctx: IndexContext,
    position_templates: dict[str, str] | None = None,
) -> str:
    """Join ``context`` with the first projected position relation (parse policies).

    Uses default Index position prose templates; does not apply compile-only medial
    exception pairing (ticket 149 / grill 150).
    """
    templates = position_templates or _DEFAULT_POSITION_TEMPLATES
    parts: list[str] = []
    if ctx.context:
        parts.append(ctx.context)
    for relation in ("adjacent_to", "near", "in"):
        projected = _project_position_relation(ctx, relation, templates)
        if projected is not None:
            parts.append(projected)
            break
    return ", ".join(parts)
