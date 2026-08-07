"""Compile-time expansion of multi-step output chains."""

from __future__ import annotations

_CHAIN_META_KEYS = ("env", "exception", "comment", "sporadic", "skip")


def expand_chained_corpus_rule(rule: dict[str, str]) -> list[dict[str, str]]:
    """Expand ``output`` chains ``a > b > c`` into sequential single-step rules.

    One corpus YAML row may compile to several ASCA rules. Rule-level ``env`` and
    ``exception`` (when present) attach to each emitted step.
    """
    output = rule.get("output", "")
    if " > " not in output:
        return [rule]
    segments = [segment.strip() for segment in output.split(" > ") if segment.strip()]
    if len(segments) < 2:
        return [rule]

    meta = {key: rule[key] for key in _CHAIN_META_KEYS if key in rule}
    expanded: list[dict[str, str]] = []
    current_input = rule["input"]
    for segment in segments:
        expanded.append({"input": current_input, "output": segment, **meta})
        current_input = segment
    return expanded
