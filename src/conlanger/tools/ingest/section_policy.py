"""Section-level ingest policies (catch-all ``else`` env resolution)."""

from __future__ import annotations

import re

from conlanger.tools.ingest.index_models import IndexContext, IndexRule
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


def _resolve_env_text(env: IndexContext | None) -> str | None:
    if env is None:
        return None
    return env.context


def resolve_catch_all_else_rules(rules: list[IndexRule]) -> list[IndexRule]:
    """Rewrite complementary ``/ else`` rules using the immediately preceding env.

    When the previous rule in the same section has ``env`` and no ``exception``,
    and that ``env`` contains ``_`` (ASCA structural focus), the else rule omits
    ``env`` (any environment) and sets ``exception`` to that previous ``env``.
    Deferred shapes (previous rule with both env and exception,
    neither, or else-after-else) keep ``env: else`` / ``else?``.
    """
    if not rules:
        return rules
    resolved_rules: list[IndexRule] = []
    for rule in rules:
        resolved = rule.model_copy(deep=True)
        env_ctx = resolved.env
        env_text = _resolve_env_text(env_ctx)
        if env_text and is_else_env_candidate(env_text):
            env_text, gloss_captures = _strip_else_env_glosses(env_text)
            if gloss_captures:
                resolved.merge_comment(*gloss_captures)
            if env_text:
                if env_ctx is not None:
                    resolved.env = env_ctx.model_copy(update={"context": env_text})
                else:
                    resolved.env = IndexContext(context=env_text)
            else:
                resolved.env = None

            if is_catch_all_else_env(env_text):
                prev = resolved_rules[-1] if resolved_rules else None
                if prev:
                    prev_env = prev.env
                    prev_env_text = _resolve_env_text(prev_env)
                    prev_exc = prev.exception

                    if (
                        prev_env is not None
                        and prev_exc is None
                        and not is_catch_all_else_env(prev_env_text or "")
                        and prev_env_text
                        and "_" in prev_env_text
                    ):
                        resolved.env = None
                        resolved.exception = prev_env.model_copy(deep=True)
        resolved_rules.append(resolved)
    return resolved_rules
