"""Section-level ingest policies (catch-all ``else`` env resolution)."""

from __future__ import annotations

import re

from conlanger.ingest.models.index_models import (
    IndexContext,
    IndexRule,
    resolve_index_context_to_string,
)
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


def _effective_env_material(env: IndexContext) -> str:
    """Env string used for catch-all ``else`` eligibility (context + position)."""
    projected = resolve_index_context_to_string(env)
    if projected:
        return projected
    if env.position and env.position.get("medial"):
        return env.context or "_"
    return env.context or ""


def _strip_else_env_glosses(env: str) -> tuple[str, list[str]]:
    """Strip trailing glosses and uncertainty qualifiers from an else env field."""
    captures: list[str] = []
    value, caps = extract_uncertainty_qualifier_from_field(env)
    captures.extend(caps)
    value, caps = extract_trailing_gloss_from_field(value)
    captures.extend(caps)
    return value.strip(), captures


def _normalize_catch_all_else_env(rule: IndexRule) -> IndexRule:
    """Strip glosses from else-shaped ``env.context``; return rule ready for complement."""
    env = rule.env
    text = env.context if env else None
    if not text or not is_else_env_candidate(text):
        return rule

    text, gloss_captures = _strip_else_env_glosses(text)
    rule.merge_comment(*gloss_captures)
    if text:
        rule.env = (
            env.model_copy(update={"context": text})
            if env is not None
            else IndexContext(context=text)
        )
    else:
        rule.env = None
    return rule


def _complement_env_from_previous(prev: IndexRule | None) -> IndexContext | None:
    """Previous rule env to use as this rule's ``exception``, or ``None`` if deferred."""
    if prev is None or prev.exception is not None or prev.env is None:
        return None
    material = _effective_env_material(prev.env)
    if not material or is_catch_all_else_env(material) or "_" not in material:
        return None
    return prev.env.model_copy(deep=True)


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

    resolved: list[IndexRule] = []
    for rule in rules:
        current = _normalize_catch_all_else_env(rule.model_copy(deep=True))
        env_text = current.env.context if current.env else None
        if env_text and is_catch_all_else_env(env_text):
            complement = (
                _complement_env_from_previous(resolved[-1]) if resolved else None
            )
            if complement is not None:
                current.env = None
                current.exception = complement
        resolved.append(current)
    return resolved
