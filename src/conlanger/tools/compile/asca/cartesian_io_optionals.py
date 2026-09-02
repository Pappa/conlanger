"""Flatten cartesian I/O optionals after parenthetical expansion (ticket 111).

Family A (optional segment prefix + parallel column): one flat ``{…}`` set.
Family B (modifier optional + parallel column): adjacent sets ``{k,kʰ}{r,j}``.
"""

from __future__ import annotations

import re

from conlanger.tools.compile.asca.sets import split_braced_set_members

_MODIFIER_CHAR_RE = re.compile(r"[\u02B0-\u02B8\u02BC\u02D1\u02E4\u0300-\u036F]")
_MAX_PASSES = 16


def _find_matching_close(text: str, open_index: int) -> int | None:
    if open_index >= len(text) or text[open_index] != "{":
        return None
    depth = 0
    for index in range(open_index, len(text)):
        char = text[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return index
    return None


def _find_matching_open(text: str, close_index: int) -> int | None:
    depth = 0
    for index in range(close_index, -1, -1):
        char = text[index]
        if char == "}":
            depth += 1
        elif char == "{":
            depth -= 1
            if depth == 0:
                return index
    return None


def _is_whole_set(text: str) -> bool:
    stripped = text.strip()
    if len(stripped) < 2 or not stripped.startswith("{") or not stripped.endswith("}"):
        return False
    close = _find_matching_close(stripped, 0)
    return close == len(stripped) - 1


def _split_trailing_set(member: str) -> tuple[str, str] | None:
    if _is_whole_set(member):
        return "", member[1:-1]
    close = member.rfind("}")
    if close != len(member) - 1:
        return None
    open_brace = _find_matching_open(member, close)
    if open_brace is None:
        return None
    return member[:open_brace], member[open_brace + 1 : close]


def _bases_are_modifier_variants(bases: list[str]) -> bool:
    non_empty = [base for base in bases if base]
    if len(non_empty) < 2 or "" in bases:
        return False
    shortest = min(non_empty, key=len)
    for base in non_empty:
        if base == shortest:
            continue
        if not base.startswith(shortest):
            return False
        suffix = base[len(shortest) :]
        if not suffix or not _MODIFIER_CHAR_RE.fullmatch(suffix):
            return False
    return True


def _rewrite_nested_set_members(inner: str) -> str | None:
    members = split_braced_set_members("{" + inner + "}")
    if not members or not any("{" in member for member in members):
        return None

    parsed: list[tuple[str, str]] = []
    inner_contents: list[str] = []
    for member in members:
        split = _split_trailing_set(member)
        if split is None:
            return None
        prefix, nested_inner = split
        parsed.append((prefix, nested_inner))
        inner_contents.append(nested_inner)

    if len(set(inner_contents)) != 1:
        return None
    shared_inner = inner_contents[0]
    inner_members = split_braced_set_members("{" + shared_inner + "}")
    if not inner_members:
        return None

    bases = [prefix for prefix, _ in parsed]
    if _bases_are_modifier_variants(bases):
        base_set = "{" + ",".join(base for base in bases if base) + "}"
        return base_set + "{" + shared_inner + "}"

    expanded: list[str] = []
    seen: set[str] = set()
    for prefix, _ in parsed:
        for item in inner_members:
            candidate = f"{prefix}{item}"
            if candidate not in seen:
                seen.add(candidate)
                expanded.append(candidate)
    return "{" + ",".join(expanded) + "}"


def _flatten_pass(text: str) -> str:
    pieces: list[str] = []
    index = 0
    while index < len(text):
        if text[index] != "{":
            pieces.append(text[index])
            index += 1
            continue
        close = _find_matching_close(text, index)
        if close is None:
            return text
        inner = text[index + 1 : close]
        rewritten = _rewrite_nested_set_members(inner)
        if rewritten is not None:
            pieces.append(rewritten)
        else:
            pieces.append("{" + inner + "}")
        index = close + 1
    return "".join(pieces)


def flatten_cartesian_io_optionals(text: str) -> str:
    """Flatten nested cartesian sets from ticket 48 into Family A/B ASCA forms."""
    if not text or "{" not in text:
        return text
    previous = text
    for _ in range(_MAX_PASSES):
        nxt = _flatten_pass(previous)
        if nxt == previous:
            return nxt
        previous = nxt
    return previous
