"""Field-token intermediate representation for ASCA compile fields (ADR-0015)."""

from __future__ import annotations

from dataclasses import dataclass

from conlanger.tools.compile.asca.sets import (
    is_whole_field_set,
    split_braced_set_members,
)
from conlanger.tools.compile.asca.structures import split_outside_groupers


@dataclass(frozen=True, slots=True)
class OptionalLengthNode:
    """Parenthesized optional length ``(ː)`` — expands before suffix length marks (ticket 104)."""

    segment: str
    suffix: str = ""
    comma_alt: str | None = None
    set_members: tuple[str, ...] | None = None


FieldToken = str | tuple[str, ...] | OptionalLengthNode


def is_set_token(token: FieldToken) -> bool:
    """True when *token* is an ordered brace-set (tuple of members)."""
    return isinstance(token, tuple)


def is_optional_length_token(token: FieldToken) -> bool:
    return isinstance(token, OptionalLengthNode)


def is_whole_field_set_tokens(tokens: tuple[FieldToken, ...]) -> bool:
    """True when the compile field is a single ordered-set field token."""
    return len(tokens) == 1 and is_set_token(tokens[0])


def token_to_raw_string(token: FieldToken) -> str:
    if is_set_token(token):
        members = token
        return "{" + ",".join(members) + "}"
    if is_optional_length_token(token):
        if token.comma_alt is not None:
            return f"{token.segment}(ː,{token.comma_alt}){token.suffix}"
        return f"{token.segment}(ː){token.suffix}"
    return token


def parse_field_tokens(raw: str) -> tuple[FieldToken, ...]:
    """Parse Index-raw compile text into an ordered field-token tuple."""
    # Lazy import: optional_length imports field_tokens types (circular at module load).
    from conlanger.tools.compile.asca.optional_length import parse_optional_length_part

    if not raw or not raw.strip():
        return ()
    tokens: list[FieldToken] = []
    for part in split_outside_groupers(raw.strip()):
        if is_whole_field_set(part):
            tokens.append(tuple(split_braced_set_members(part)))
        else:
            tokens.append(parse_optional_length_part(part))
    return tuple(tokens)


def render_field_tokens(tokens: tuple[FieldToken, ...]) -> str:
    """Join field tokens back into Index-raw compile-field text."""
    if not tokens:
        return ""
    return " ".join(token_to_raw_string(token) for token in tokens)


def set_token_members(token: FieldToken) -> list[str]:
    """Return ordered brace members for a set token; empty for non-sets."""
    if is_set_token(token):
        return list(token)
    return []


def is_optional_output_shape(
    input_tokens: tuple[FieldToken, ...],
    output_tokens: tuple[FieldToken, ...],
) -> bool:
    """Whole-field output set with unpaired input (ticket 66)."""
    if not is_whole_field_set_tokens(output_tokens):
        return False
    if is_whole_field_set_tokens(input_tokens):
        return False
    members = set_token_members(output_tokens[0])
    return bool(members) and all(member and "{" not in member for member in members)


def set_contains_null_member(token: FieldToken) -> bool:
    null_tokens = frozenset({"∅", "Ø", "0", "*"})
    if is_set_token(token):
        return any(member in null_tokens for member in token)
    return False
