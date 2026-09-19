"""Flatten nested Index ``{}`` sets in env / exception / stages (parse-time P4).

ASCA 0.10.2 rejects nested brackets of the same type (``NestedBrackets``).
Index env/exception/stages often encode union of members with nested braces;
this helper rewrites those to a single-level set. Unbalanced strings are left
unchanged. ``raw`` is never mutated (callers apply this to working fields).
"""

from __future__ import annotations

from typing import Any

from conlanger.utils.bracket_scanner import (
    BRACES,
    is_brace_wrapped,
    split_outside_brackets,
)

_MAX_PASSES = 16


def flatten_nested_sets(text: str) -> str:
    """Flatten same-type nested ``{}`` using union + parenthetical-in-set.

    ``{a,{b,c}}`` → ``{a,b,c}``; ``({m,j,w})V`` → ``{mV,jV,wV}``;
    ``(C){p,kʷ}`` as a set member → ``(C)p,(C)kʷ``. Top-level
    ``(h)ə{p,b}`` is unchanged. Flat sets are not re-serialized.
    Field-level ``({set})X`` with no nested braces is left unchanged.
    """
    if not text or "{" not in text:
        return text
    if not BRACES.is_balanced(text):
        return text
    previous = text
    for _ in range(_MAX_PASSES):
        nxt = _flatten_pass(previous)
        if nxt == previous:
            return nxt
        if not BRACES.is_balanced(nxt):
            return previous
        previous = nxt
    return previous


def flatten_nested_sets_in_rule_fields(rule: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``rule`` with ``env`` / ``exception`` / ``stages`` flattened."""
    updated = dict(rule)
    for key in ("env", "exception"):
        if key not in updated or not updated[key]:
            continue
        original = str(updated[key])
        updated[key] = flatten_nested_sets(original)
    stages = updated.get("stages")
    if stages:
        updated["stages"] = [
            flatten_nested_sets(stage) if stage else stage for stage in stages
        ]
    return updated


def flatten_nested_sets_in_section_rules(
    rules: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Flatten env/exception/stages on each rule (after else resolution)."""
    return [flatten_nested_sets_in_rule_fields(rule) for rule in rules]


def _flatten_pass(text: str) -> str:
    if BRACES.max_depth(text) >= 2:
        text = _expand_paren_wrapped_sets(text)
    return _flatten_sets_in_string(text)


def _split_members(inner: str) -> list[str]:
    return split_outside_brackets(
        inner,
        ",",
        strip_parts=True,
        flush_on_separator="always",
        omit_empty_tail=True,
    )


def _is_whole_set(text: str) -> bool:
    stripped = text.strip()
    if not is_brace_wrapped(stripped):
        return False
    close = BRACES.closing_index(stripped, 0)
    return close == len(stripped) - 1


def _try_distribute(member: str) -> list[str] | None:
    spans = BRACES.top_level_spans(member)
    if len(spans) != 1:
        return None
    start, end = spans[0]
    set_text = member[start:end]
    prefix, suffix = member[:start], member[end:]
    if prefix == "" and suffix == "":
        return None
    inner_members = _split_members(set_text[1:-1])
    if not inner_members:
        return None
    if prefix.endswith("(") and suffix.startswith(")"):
        rest = suffix[1:]
        return [f"{item}{rest}" for item in inner_members]
    return [f"{prefix}{item}{suffix}" for item in inner_members]


def _flatten_sets_in_string(text: str) -> str:
    pieces: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "{":
            close = BRACES.closing_index(text, index)
            if close is None:
                return text
            inner = text[index + 1 : close]
            pieces.append("{" + _rewrite_set_inner(inner) + "}")
            index = close + 1
        else:
            pieces.append(text[index])
            index += 1
    return "".join(pieces)


def _rewrite_set_inner(inner: str) -> str:
    # Do not re-serialize a flat set (preserves spacing in e.g. ASCA env-sets
    # ``:{#_, _#}:``). Only rewrite when an inner ``{`` is present.
    if "{" not in inner:
        return inner
    out: list[str] = []
    for member in _split_members(inner) or [inner]:
        rewritten = _flatten_sets_in_string(member)
        if _is_whole_set(rewritten):
            out.extend(_split_members(rewritten.strip()[1:-1]))
            continue
        distributed = _try_distribute(rewritten)
        if distributed is not None:
            out.extend(distributed)
            continue
        out.append(rewritten)
    return ",".join(out)


def _expand_paren_wrapped_sets(text: str) -> str:
    """Expand ``({a,b})X`` outside of (and inside) set members."""
    if "({" not in text:
        return text
    pieces: list[str] = []
    index = 0
    length = len(text)
    while index < length:
        if text.startswith("({", index):
            close = BRACES.closing_index(text, index + 1)
            if close is not None and close + 1 < length and text[close + 1] == ")":
                tail_start = close + 2
                tail_end = _consume_segment_tail(text, tail_start)
                if tail_end > tail_start:
                    inner = text[index + 2 : close]
                    members = _split_members(inner)
                    tail = text[tail_start:tail_end]
                    expanded = "{" + ",".join(f"{item}{tail}" for item in members) + "}"
                    pieces.append(expanded)
                    index = tail_end
                    continue
        pieces.append(text[index])
        index += 1
    return "".join(pieces)


def _consume_segment_tail(text: str, start: int) -> int:
    """Consume a following segment / class letter / optional ``[...]`` matrix."""
    index = start
    length = len(text)
    while index < length:
        char = text[index]
        if char in "{}\n,/_#!| ":
            break
        if char == "[":
            close = text.find("]", index)
            if close == -1:
                break
            index = close + 1
            continue
        if char == "(":
            break
        index += 1
    return index
