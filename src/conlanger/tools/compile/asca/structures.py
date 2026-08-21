"""Top-level ASCA field and token structure helpers."""

from __future__ import annotations

OUTPUT_SEPARATOR = " > "
ENV_SEPARATOR = " / "
EXCEPTION_SEPARATOR = " // "


def split_outside_groupers(text: str, sep: str = " ") -> list[str]:
    """Split on ``sep`` outside ``{}``, ``()``, and ``[]`` groupers."""
    parts: list[str] = []
    current: list[str] = []
    depth_brace = 0
    depth_paren = 0
    depth_bracket = 0
    for ch in text:
        if ch == "{":
            depth_brace += 1
        elif ch == "}":
            depth_brace -= 1
        elif ch == "(":
            depth_paren += 1
        elif ch == ")":
            depth_paren -= 1
        elif ch == "[":
            depth_bracket += 1
        elif ch == "]":
            depth_bracket -= 1
        if ch == sep and depth_brace == 0 and depth_paren == 0 and depth_bracket == 0:
            if current:
                parts.append("".join(current))
                current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current))
    return parts


def join_asca_rule_fields(
    inp: str,
    output: str,
    env: str | None = None,
    exception: str | None = None,
) -> str:
    """Join compiled ASCA rule fields for render."""
    result = inp + OUTPUT_SEPARATOR + output
    if env:
        result += ENV_SEPARATOR + env
    if exception:
        result += EXCEPTION_SEPARATOR + exception
    return result
