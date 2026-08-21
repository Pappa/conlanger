"""Compile-time expansion of multi-step change spines."""

from __future__ import annotations

_CHAIN_META_KEYS = ("env", "exception", "comment", "sporadic")


def expand_chained_corpus_rule(rule: dict[str, str]) -> list[dict[str, str]]:
    """Expand corpus ``stages`` into sequential single-step ASCA rules.

    One corpus YAML row may compile to several ASCA rules. Rule-level ``env`` and
    ``exception`` (when present) attach to each emitted step. Empty ``stages`` emit
    nothing.
    """
    stages = rule.get("stages", [])
    non_empty = [stage.strip() for stage in stages if stage and stage.strip()]
    if len(non_empty) < 2:
        return []

    meta = {key: rule[key] for key in _CHAIN_META_KEYS if key in rule}
    expanded: list[dict[str, str]] = []
    for index in range(len(non_empty) - 1):
        expanded.append(
            {
                "input": non_empty[index],
                "output": non_empty[index + 1],
                **meta,
            }
        )
    return expanded
