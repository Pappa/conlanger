"""Naive nested-``{}`` flatten for spike 85 (throwaway).

Not production parser/compiler code. Scope is documented in
``nested-set-flatten-prototype.md``.

Run self-check: ``uv run python .scratch/rule-index/research/flatten_nested_sets.py``
"""

from __future__ import annotations

from typing import Any

MODE_UNION = "union"
MODE_UNION_PAREN = "union_paren"

_MAX_PASSES = 16


def brace_balance(text: str) -> int:
    depth = 0
    for char in text:
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return depth
    return depth


def is_unbalanced_braces(text: str) -> bool:
    return brace_balance(text) != 0


def flatten_nested_sets(text: str, *, mode: str = MODE_UNION) -> str:
    """Flatten same-type nested ``{}``; leave malformed strings unchanged.

    ``mode='union'``: splice complete nested set members and distribute
    non-parenthetical prefix/suffix over an inner set (``{a,{b,c}}``,
    ``{h,k,ŋ}n``). Does **not** expand ``({m,j,w})V`` or ``(C){p,kʷ}``.

    ``mode='union_paren'``: also expand parenthetical-in-set shapes
    ``({a,b})X`` → ``{aX,bX}`` and ``(X){a,b}`` → ``{(X)a,(X)b}`` when those
    occur as set members (or, for the wrapped-set form, anywhere).

    Top-level ``segment{variants}`` / ``(h)ə{p,b}`` is out of scope: those
    are not members of an outer ``{}``.
    """
    if not text or "{" not in text:
        return text
    if is_unbalanced_braces(text):
        return text
    if mode not in {MODE_UNION, MODE_UNION_PAREN}:
        raise ValueError(f"unknown flatten mode {mode!r}")
    previous = text
    for _ in range(_MAX_PASSES):
        nxt = _flatten_pass(previous, mode=mode)
        if nxt == previous:
            return nxt
        if is_unbalanced_braces(nxt):
            return previous
        previous = nxt
    return previous


def apply_flatten_to_parts(
    parts: dict[str, Any] | None,
    *,
    mode: str = MODE_UNION,
) -> dict[str, Any] | None:
    """Flatten ``stages`` / ``env`` / ``exception`` on a parse-parts dict."""
    if parts is None:
        return None
    updated, _changed = apply_flatten_to_rule(parts, mode=mode)
    return updated


def apply_flatten_to_rule(
    rule: dict[str, Any],
    *,
    mode: str = MODE_UNION,
) -> tuple[dict[str, Any], list[str]]:
    """Return ``(new_rule, changed_field_names)``. Never mutates ``raw``."""
    new_rule = dict(rule)
    changed: list[str] = []
    stages = rule.get("stages")
    if isinstance(stages, list):
        new_stages: list[Any] = []
        for index, stage in enumerate(stages):
            if stage is None or not str(stage):
                new_stages.append(stage)
                continue
            original = str(stage)
            flattened = flatten_nested_sets(original, mode=mode)
            if flattened != original:
                changed.append(f"stages[{index}]")
            new_stages.append(flattened)
        new_rule["stages"] = new_stages
    for key in ("env", "exception"):
        if key not in rule or rule[key] in (None, ""):
            continue
        original = str(rule[key])
        flattened = flatten_nested_sets(original, mode=mode)
        if flattened != original:
            changed.append(key)
        new_rule[key] = flattened
    return new_rule, changed


def _flatten_pass(text: str, *, mode: str) -> str:
    if mode == MODE_UNION_PAREN:
        text = _expand_paren_wrapped_sets(text)
    return _flatten_sets_in_string(text, mode=mode)


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


def _has_paren(prefix: str, suffix: str) -> bool:
    return any(char in prefix or char in suffix for char in "()")


def _try_distribute(member: str, *, mode: str) -> list[str] | None:
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
    if mode == MODE_UNION:
        if _has_paren(prefix, suffix):
            return None
        return [f"{prefix}{item}{suffix}" for item in inner_members]
    if _paren_wraps_set(prefix, suffix):
        rest = suffix[1:]
        return [f"{item}{rest}" for item in inner_members]
    return [f"{prefix}{item}{suffix}" for item in inner_members]


def _flatten_sets_in_string(text: str, *, mode: str) -> str:
    pieces: list[str] = []
    index = 0
    while index < len(text):
        if text[index] == "{":
            close = _match_brace(text, index)
            if close is None:
                return text
            inner = text[index + 1 : close]
            pieces.append("{" + _rewrite_set_inner(inner, mode=mode) + "}")
            index = close + 1
        else:
            pieces.append(text[index])
            index += 1
    return "".join(pieces)


def _rewrite_set_inner(inner: str, *, mode: str) -> str:
    # Do not re-serialize a flat set (preserves spacing in e.g. ASCA env-sets
    # ``:{#_, _#}:``). Only rewrite when an inner ``{`` is present.
    if "{" not in inner:
        return inner
    out: list[str] = []
    for member in _split_members(inner) or [inner]:
        rewritten = _flatten_sets_in_string(member, mode=mode)
        if _is_whole_set(rewritten):
            out.extend(_split_members(rewritten.strip()[1:-1]))
            continue
        distributed = _try_distribute(rewritten, mode=mode)
        if distributed is not None:
            out.extend(distributed)
            continue
        out.append(rewritten)
    return ",".join(out)


def _expand_paren_wrapped_sets(text: str) -> str:
    """Expand ``({a,b})X`` outside of (and inside) set members.

    ``(C){p,kʷ}`` is handled by distribution inside a set, not here.
    """
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


_SELF_CHECKS: list[tuple[str, str, str]] = [
    ("{a,{b,c}}", MODE_UNION, "{a,b,c}"),
    ("{ʔ,{h1,h2}}", MODE_UNION, "{ʔ,h1,h2}"),
    ("{{h,k,ŋ}n,w,v,l,r}_", MODE_UNION, "{hn,kn,ŋn,w,v,l,r}_"),
    ("{a{o,e},aC{o,e}}", MODE_UNION, "{ao,ae,aCo,aCe}"),
    ("#_{xʲ,w{i,a},qʷa}", MODE_UNION, "#_{xʲ,wi,wa,qʷa}"),
    ("{{C[-fr,+bk,-hi,-lo],K}ʷ,w}_", MODE_UNION, "{C[-fr,+bk,-hi,-lo]ʷ,Kʷ,w}_"),
    ("(h)ə{p,b}", MODE_UNION, "(h)ə{p,b}"),
    ("(h)ə{p,b}", MODE_UNION_PAREN, "(h)ə{p,b}"),
    ("_{s,({m,j,w})V}", MODE_UNION, "_{s,({m,j,w})V}"),
    ("_{s,({m,j,w})V}", MODE_UNION_PAREN, "_{s,mV,jV,wV}"),
    ("_ə{(C){p,kʷ},m,w}", MODE_UNION, "_ə{(C){p,kʷ},m,w}"),
    ("_ə{(C){p,kʷ},m,w}", MODE_UNION_PAREN, "_ə{(C)p,(C)kʷ,m,w}"),
    ("{hə{p,b},ə{p,b}}", MODE_UNION, "{həp,həb,əp,əb}"),
    (
        "e o u æ ø y → {a,e} {o,u} {a,o,u a {a,o,u} {o,u,i}",
        MODE_UNION,
        "e o u æ ø y → {a,e} {o,u} {a,o,u a {a,o,u} {o,u,i}",
    ),
    ("{{∅,∅}s,s{∅,∅}}", MODE_UNION, "{∅s,∅s,s∅,s∅}"),
    (":{#_, _#}:", MODE_UNION, ":{#_, _#}:"),
    ("{a, b, c}", MODE_UNION, "{a, b, c}"),
]


def main() -> None:
    failed = 0
    for source, mode, expected in _SELF_CHECKS:
        got = flatten_nested_sets(source, mode=mode)
        status = "ok" if got == expected else "FAIL"
        if got != expected:
            failed += 1
        print(
            f"{status:4} [{mode}] {source!r} → {got!r}"
            + ("" if got == expected else f" (want {expected!r})")
        )
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
