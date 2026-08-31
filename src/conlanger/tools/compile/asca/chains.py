"""Compile-time expansion of multi-step change spines."""

from __future__ import annotations

_CHAIN_META_KEYS = ("env", "exception", "comment", "sporadic")


def expand_chained_index_rule(rule: dict[str, str]) -> list[dict[str, str]]:
    """Expand index ``stages`` into sequential single-step ASCA rules.

    One index YAML row may compile to several ASCA rules. Rule-level ``env`` and
    ``exception`` (when present) attach to each emitted step. A single non-empty
    stage compiles to one rule with empty output. Empty ``stages`` emit nothing.
    """
    stages = rule.get("stages", [])
    non_empty = [str(stage).strip() for stage in stages if stage and str(stage).strip()]
    meta = {key: rule[key] for key in _CHAIN_META_KEYS if key in rule}
    if len(non_empty) == 0:
        return []
    if len(non_empty) == 1:
        return [{"input": non_empty[0], "output": "", **meta}]
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
