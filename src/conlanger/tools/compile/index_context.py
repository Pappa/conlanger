"""Resolve structured ``IndexContext`` to ASCA env/exception strings (ADR-0017)."""

from __future__ import annotations

from typing import Any

from conlanger.tools.ingest.index_models import IndexContext

EnvExceptionInput = str | IndexContext | dict[str, Any]


def resolve_index_context_to_string(ctx: IndexContext) -> str:
    """Project ``IndexContext`` to a single env/exception string for compile.

    Full position/dialect resolution expands in ticket 144; v1 uses ``context``
    when present and ignores ``dialect`` until render gating is specified.
    """
    if ctx.context:
        return ctx.context
    if ctx.position:
        adjacent = ctx.position.get("adjacent_to")
        if isinstance(adjacent, str) and len(adjacent) == 1:
            return f"{adjacent}_, _{adjacent}"
        if isinstance(adjacent, list) and len(adjacent) == 1 and len(adjacent[0]) == 1:
            char = adjacent[0]
            return f"{char}_, _{char}"
    return ""


def env_exception_input_to_string(value: EnvExceptionInput) -> str:
    """Coerce YAML ``env`` / ``exception`` field to a compile string."""
    if isinstance(value, str):
        return value
    ctx = (
        value if isinstance(value, IndexContext) else IndexContext.model_validate(value)
    )
    return resolve_index_context_to_string(ctx)
