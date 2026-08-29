"""Flatten nested Index ``{}`` sets in env / exception (parse-time P4).

ASCA 0.10.2 rejects nested brackets of the same type (``NestedBrackets``).
Index env/exception often encode union of members with nested braces; this
helper rewrites those to a single-level set. Unbalanced strings are left
unchanged. ``raw`` is never mutated (callers apply this to working fields).
"""

from __future__ import annotations

from typing import Any

_MAX_PASSES = 16


def flatten_nested_sets(text: str) -> str:
    """Flatten same-type nested ``{}`` using union + parenthetical-in-set.

    ``{a,{b,c}}`` → ``{a,b,c}``; ``({m,j,w})V`` → ``{mV,jV,wV}``;
    ``(C){p,kʷ}`` as a set member → ``(C)p,(C)kʷ``. Top-level
    ``(h)ə{p,b}`` is unchanged. Flat sets are not re-serialized.
    Field-level ``({set})X`` with no nested braces is left unchanged.
    """
    return _flatten_nested_sets(text)


def flatten_nested_sets_in_context_fields(rule: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of ``rule`` with ``env`` / ``exception`` flattened."""
    updated = dict(rule)
    for key in ("env", "exception"):
        if key not in updated or updated[key] in (None, ""):
            continue
        original = str(updated[key])
        updated[key] = flatten_nested_sets(original)
    return updated


def flatten_nested_sets_in_section_rules(
    rules: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Flatten env/exception on each rule (after else resolution)."""
    return [flatten_nested_sets_in_context_fields(rule) for rule in rules]


def _flatten_nested_sets(text: str) -> str:
    if not text or "{" not in text:
        return text
    if _is_unbalanced_braces(text):
        return text
    previous = text
    for _ in range(_MAX_PASSES):
        nxt = _flatten_pass(previous)
        if nxt == previous:
            return nxt
        if _is_unbalanced_braces(nxt):
            return previous
        previous = nxt
    return previous


def _brace_balance(text: str) -> int:
    depth = 0
    for char in text:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return depth
    return depth


def _is_unbalanced_braces(text: str) -> bool:
    return _brace_balance(text) != 0


def _flatten_pass(text: str) -> str:
    if _max_brace_depth(text) >= 2:
        text = _expand_paren_wrapped_sets(text)
    return _flatten_sets_in_string(text)


def _max_brace_depth(text: str) -> int:
    depth = 0
    maximum = 0
    for char in text:
        if char == "{":
            depth += 1
            maximum = max(maximum, depth)
        elif char == "}":
            depth -= 1
    return maximum


def _match_brace(text: str, start: int) -> int | None:
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    for index in range(start, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def _split_members(inner: str) -> list[str]:
    members: list[str] = []
    current: list[str] = []
    depth_brace = depth_paren = depth_bracket = 0
    for char in inner:
        if char == "{":
            depth_brace += 1
        elif char == "}":
            depth_brace -= 1
        elif char == "(":
            depth_paren += 1
        elif char == ")":
            depth_paren -= 1
        elif char == "[":
            depth_bracket += 1
        elif char == "]":
            depth_bracket -= 1
        if char == "," and depth_brace == 0 and depth_paren == 0 and depth_bracket == 0:
            members.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    tail = "".join(current).strip()
    if tail:
        members.append(tail)
    return members


def _is_whole_set(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 2 or not stripped.startswith("{") or not stripped.endswith("}"):
        return False
    close = _match_brace(stripped, 0)
    return close == len(stripped) - 1


def _top_level_sets(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    index = 0
    while index < len(text):
        if text[index] == "{":
            close = _match_brace(text, index)
            if close is None:
                return []
            spans.append((index, close + 1))
            index = close + 1
        else:
            index += 1
    return spans


def _paren_wraps_set(prefix: str, suffix: str) -> bool:
    return prefix.endswith("(") and suffix.startswith(")")


def _try_distribute(member: str) -> list[str] | None:
    spans = _top_level_sets(member)
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
    if _paren_wraps_set(prefix, suffix):
        rest = suffix[1:]
        return [f"{item}{rest}" for item in inner_members]
    return [f"{prefix}{item}{suffix}" for item in inner_members]


def _flatten_sets_in_string(text: str) -> str:
    pieces: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "{":
            close = _match_brace(text, index)
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
            close = _match_brace(text, index + 1)
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
