"""Section-level ingest policies (catch-all ``else`` env resolution)."""

from __future__ import annotations

import re
from typing import Any

from conlanger.tools.ingest.transforms import append_rule_comment_parts
from conlanger.utils.gloss import (
    extract_trailing_gloss_from_field,
    extract_uncertainty_qualifier_from_field,
)

_CATCH_ALL_ELSE_ENV_RE = re.compile(r"^\s*else\??\s*$", re.IGNORECASE)
_ELSE_ENV_CANDIDATE_RE = re.compile(r"\belse\b", re.IGNORECASE)


def is_catch_all_else_env(env: str) -> bool:
    """Return whether ``env`` is a bare Index catch-all ``else`` / ``else?``."""
    return bool(env and _CATCH_ALL_ELSE_ENV_RE.match(env))


def is_else_env_candidate(env: str) -> bool:
    """Return whether ``env`` is a candidate for a catch-all ``else`` / ``else?``."""
    return bool(env and _ELSE_ENV_CANDIDATE_RE.search(env))


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
    and that ``env`` contains ``_`` (ASCA structural focus), the else rule omits
    ``env`` (any environment) and sets ``exception`` to that previous ``env``.
    Deferred shapes (previous rule with both env and exception,
    neither, or else-after-else) keep ``env: else`` / ``else?``.
    """
    if not rules:
        return rules
    resolved_rules: list[dict[str, Any]] = []
    for rule in rules:
        resolved = dict(rule)
        env = resolved.get("env")
        env_text = _resolve_env_text(env)
        if env_text and is_else_env_candidate(env_text):
            env_text, gloss_captures = _strip_else_env_glosses(env_text)
            if gloss_captures:
                append_rule_comment_parts(resolved, gloss_captures)
            if env_text:
                if isinstance(env, dict):
                    env["context"] = env_text
                    resolved["env"] = env
                else:
                    resolved["env"] = env_text
            elif "env" in resolved:
                del resolved["env"]

            if is_catch_all_else_env(env_text):
                prev = resolved_rules[-1] if resolved_rules else None
                if prev:
                    prev_env = prev.get("env")
                    prev_env_text = _resolve_env_text(prev_env)
                    prev_exc = prev.get("exception")

                    if (
                        prev_env
                        and not prev_exc
                        and not is_catch_all_else_env(prev_env_text)
                        and "_" in prev_env
                    ):
                        resolved = {
                            key: value
                            for key, value in resolved.items()
                            if key != "env"
                        }
                        resolved["exception"] = prev_env
        resolved_rules.append(resolved)
    return resolved_rules


def _resolve_env_text(env: str | dict[str, Any] | None) -> str | None:
    if env and isinstance(env, dict):
        return env.get("context")
    return env
