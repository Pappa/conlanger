"""Project structured ``IndexContext`` to compile env/exception strings."""

from __future__ import annotations

from conlanger.compile.models.config import PositionTemplates
from conlanger.compile.position_in_projection import (
    materialize_position_in_asca,
    project_position_in_target,
)
from conlanger.ingest.models.index_models import (
    EnvExceptionInput,
    IndexContext,
    PositionValue,
)
from conlanger.utils.transform_fields import MEDIAL_BOUNDARY_EXCEPTION

DEFAULT_POSITION_TEMPLATES: dict[str, str] = PositionTemplates().model_dump(
    by_alias=True
)


def _position_target_value(value: PositionValue) -> str | None:
    if isinstance(value, list):
        if not value:
            return None
        value = value[0]
    if isinstance(value, str) and value:
        return value
    return None


def _project_double_slash_position(ctx: IndexContext) -> str | None:
    """Project ticket-108 structured ``position`` keys to ASCA exception/env tails."""
    if not ctx.position:
        return None
    if ctx.position.get("penult"):
        return "%_"
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


def resolve_index_context_to_string(
    ctx: IndexContext,
    position_templates: dict[str, str] | None = None,
) -> str:
    """Project ``IndexContext`` to a compile env/exception string.

    Joins structural ``context`` with the first projected position relation
    (``adjacent_to``, then ``near``, then ``in``) using comma separation.
    Rule-level medial pairing is applied in ``resolve_rule_env_exception_for_compile``
    (called from compile ``materialize_index_rule_env_exception``, not ``SoundChangeRule``).
    """
    templates = position_templates or DEFAULT_POSITION_TEMPLATES
    parts: list[str] = []
    if ctx.context:
        parts.append(ctx.context)
    double_slash = _project_double_slash_position(ctx)
    if double_slash is not None:
        parts.append(double_slash)
        return ", ".join(parts)
    for relation in ("adjacent_to", "near", "in"):
        if relation == "in":
            target = _position_target_value(
                ctx.position.get("in") if ctx.position else None
            )
            if target is None or templates.get("in") is None:
                continue
            classified = project_position_in_target(target)
            if classified is not None:
                return materialize_position_in_asca(
                    classified,
                    structural_context=ctx.context or None,
                )
            projected = templates["in"].format(v=target)
        else:
            projected = _project_position_relation(ctx, relation, templates)
        if projected is not None:
            parts.append(projected)
            break
    return ", ".join(parts)


def _coerce_optional_index_context(
    value: EnvExceptionInput | None,
) -> IndexContext | None:
    if value is None:
        return None
    if isinstance(value, IndexContext):
        return value
    if isinstance(value, str):
        return IndexContext.model_validate({"context": value})
    if isinstance(value, dict):
        return IndexContext.model_validate(value)
    raise TypeError(f"Invalid env/exception value: {value!r}")


def merge_medial_boundary_exception(exc_str: str | None) -> str:
    """Combine compile exception text with medial boundary ``#_, _#`` (ticket 149 Q5)."""
    if not exc_str:
        return MEDIAL_BOUNDARY_EXCEPTION
    if MEDIAL_BOUNDARY_EXCEPTION in exc_str:
        return exc_str
    return f"{exc_str}, {MEDIAL_BOUNDARY_EXCEPTION}"


def resolve_rule_env_exception_for_compile(
    env: EnvExceptionInput | None,
    exception: EnvExceptionInput | None,
    *,
    position_templates: dict[str, str] | None = None,
) -> tuple[str | None, str | None]:
    """Project rule-level ``env`` / ``exception`` to compile strings (ticket 144)."""
    env_ctx = _coerce_optional_index_context(env)
    exc_ctx = _coerce_optional_index_context(exception)

    env_str: str | None = None
    exc_str: str | None = None

    if env_ctx is not None:
        env_str = resolve_index_context_to_string(env_ctx, position_templates) or None
        if (
            env_ctx.position
            and env_ctx.position.get("medial")
            and exc_ctx is None
            and not env_str
        ):
            env_str = "_"
    if exc_ctx is not None:
        exc_str = resolve_index_context_to_string(exc_ctx, position_templates) or None

    if env_ctx is not None and env_ctx.position and env_ctx.position.get("medial"):
        exc_str = merge_medial_boundary_exception(exc_str)

    return env_str, exc_str


def env_exception_input_to_string(
    value: EnvExceptionInput,
    *,
    position_templates: dict[str, str] | None = None,
) -> str:
    """Coerce YAML ``env`` / ``exception`` field to a compile string."""
    if isinstance(value, str):
        return value
    ctx = (
        value if isinstance(value, IndexContext) else IndexContext.model_validate(value)
    )
    return resolve_index_context_to_string(ctx, position_templates)
