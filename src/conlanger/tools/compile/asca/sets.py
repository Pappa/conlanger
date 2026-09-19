"""Brace-set helpers for ASCA compile (whole-field sets, member splitting)."""

from __future__ import annotations

from conlanger.utils.bracket_scanner import (
    BRACES,
    BRACKETS,
    PARENS,
    is_brace_wrapped,
    split_outside_brackets,
)


def is_whole_field_set(text: str) -> bool:
    """True when ``text`` is a single ``{…}`` set spanning the whole field."""
    stripped = text.strip()
    if not is_brace_wrapped(stripped):
        return False
    close = BRACES.closing_index(stripped, 0)
    if close is None:
        return False
    return close == len(stripped) - 1


def convert_set_to_environment_set(text: str) -> str:
    """Convert a ``{…}`` set to an environment set (e.g. ``{…}`` → ``:{…}:``)."""
    return f":{text}:"


def split_braced_set_members(set_text: str) -> list[str]:
    """Split a ``{…}`` set string into top-level members (nested ``{…}`` aware)."""
    inner = set_text.strip()[1:-1]
    return split_outside_brackets(
        inner,
        ",",
        respect=(BRACES,),
        strip_parts=True,
        flush_on_separator="always",
    )


def split_set_members(content: str) -> list[str]:
    """Split set inner content on commas outside ``(…)`` and ``[…]`` groupers."""
    return split_outside_brackets(
        content,
        ",",
        respect=(PARENS, BRACKETS),
        strip_parts=True,
        flush_on_separator="always",
        omit_empty_tail=True,
    )
