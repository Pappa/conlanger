"""Top-level ASCA field and token structure helpers."""

from __future__ import annotations

from conlanger.utils.bracket_scanner import split_outside_brackets

OUTPUT_SEPARATOR = " > "
ENV_SEPARATOR = " / "
EXCEPTION_SEPARATOR = " // "


def split_outside_groupers(text: str, sep: str = " ") -> list[str]:
    """Split on ``sep`` outside ``{}``, ``()``, and ``[]`` groupers."""
    return split_outside_brackets(text, sep)


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
