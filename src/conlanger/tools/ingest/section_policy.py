"""Section-level ingest policies (catch-all ``else`` env resolution)."""

from __future__ import annotations

import re
from typing import Any

from conlanger.tools.ingest.transforms import _append_rule_comment_parts
from conlanger.utils.gloss import (
    extract_trailing_gloss_from_field,
    extract_uncertainty_qualifier_from_field,
)

_CATCH_ALL_ELSE_ENV_RE = re.compile(r"^\s*else\??\s*$", re.IGNORECASE)
_ELSE_ENV_CANDIDATE_RE = re.compile(r"\belse\b", re.IGNORECASE)


def is_catch_all_else_env(env: str) -> bool:
    """Return whether ``env`` is a bare Index catch-all ``else`` / ``else?``."""
    return bool(env and _CATCH_ALL_ELSE_ENV_RE.match(env))


def _strip_else_env_glosses(env: str) -> tuple[str, list[str]]:
    """Strip trailing glosses and uncertainty qualifiers from an else env field."""
    captures: list[str] = []
    value, caps = extract_uncertainty_qualifier_from_field(env)
    captures.extend(caps)
    value, caps = extract_trailing_gloss_from_field(value)
    captures.extend(caps)
    return value.strip(), captures


def resolve_catch_all_else_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Rewrite complementary ``/ else`` rules using the immediately preceding env.

    When the previous rule in the same section has ``env`` and no ``exception``,
    the else rule omits ``env`` (any environment) and sets ``exception`` to that
    previous ``env``. Deferred shapes (previous rule with both env and exception,
    neither, or else-after-else) keep ``env: else`` / ``else?``.
    """
    if not rules:
        return rules
    resolved_rules: list[dict[str, Any]] = []
    for rule in rules:
        resolved = dict(rule)
        env = resolved.get("env")
        if env and _ELSE_ENV_CANDIDATE_RE.search(env):
            env, gloss_captures = _strip_else_env_glosses(env)
            if gloss_captures:
                _append_rule_comment_parts(resolved, gloss_captures)
            if env:
                resolved["env"] = env
            elif "env" in resolved:
                del resolved["env"]

            if is_catch_all_else_env(env):
                prev = resolved_rules[-1] if resolved_rules else None
                if prev:
                    prev_env = prev.get("env")
                    prev_exc = prev.get("exception")
                    if (
                        prev_env
                        and not prev_exc
                        and not is_catch_all_else_env(prev_env)
                    ):
                        resolved = {
                            key: value
                            for key, value in resolved.items()
                            if key != "env"
                        }
                        resolved["exception"] = prev_env
        resolved_rules.append(resolved)
    return resolved_rules
