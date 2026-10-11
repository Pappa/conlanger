"""Materialize index YAML rule dicts for compile-time ``SoundChangeRule``."""

from __future__ import annotations

from typing import Any

from conlanger.ingest.models.index_models import resolve_rule_env_exception_for_compile
from conlanger.ingest.models.mappings import CompilerConfig


def materialize_index_rule_env_exception(
    rule: dict[str, Any],
    *,
    compiler_config: CompilerConfig,
) -> dict[str, Any]:
    """Replace structured ``env`` / ``exception`` mappings with compile strings."""
    env = rule.get("env")
    exception = rule.get("exception")
    if not isinstance(env, dict) and not isinstance(exception, dict):
        return rule

    templates = compiler_config.position_templates.model_dump()
    env_str, exc_str = resolve_rule_env_exception_for_compile(
        env, exception, position_templates=templates
    )
    result = dict(rule)
    if env is not None:
        result["env"] = env_str
    if exception is not None or exc_str is not None:
        result["exception"] = exc_str
    return result
