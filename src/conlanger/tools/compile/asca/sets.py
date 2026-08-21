"""Brace-set helpers for ASCA compile (whole-field sets, member splitting)."""

from __future__ import annotations


def is_whole_field_set(text: str) -> bool:
    """True when ``text`` is a single ``{…}`` set spanning the whole field."""
    stripped = text.strip()
    if len(stripped) < 2 or not stripped.startswith("{") or not stripped.endswith("}"):
        return False
    depth = 0
    for position, char in enumerate(stripped):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False
            if depth == 0 and position != len(stripped) - 1:
                return False
    return depth == 0


def split_braced_set_members(set_text: str) -> list[str]:
    """Split a ``{…}`` set string into top-level members (nested ``{…}`` aware)."""
    inner = set_text.strip()[1:-1]
    members: list[str] = []
    current: list[str] = []
    depth = 0
    for char in inner:
        if char == "{":
            depth += 1
            current.append(char)
        elif char == "}":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            members.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    members.append("".join(current).strip())
    return members


def split_set_members(content: str) -> list[str]:
    """Split set inner content on commas outside ``(…)`` and ``[…]`` groupers."""
    members: list[str] = []
    current: list[str] = []
    depth_paren = 0
    depth_bracket = 0
    for ch in content:
        if ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1
        elif ch == "[":
            depth_bracket += 1
        elif ch == "]":
            depth_bracket -= 1
        if ch == "," and depth_paren == 0 and depth_bracket == 0:
            members.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    tail = "".join(current).strip()
    if tail:
        members.append(tail)
    return members
