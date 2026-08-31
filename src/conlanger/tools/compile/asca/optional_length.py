"""Parenthesized optional length ``(ː)`` expansion (ticket 104 / ADR-0015).

Expands optional-length notation to ordered alternation ``{short, long}`` before
suffix ``length_marks`` run. Matrix and template analogues add ``+long`` inside
feature brackets; bare segments use ``:[+long]``.
"""

from __future__ import annotations

import re

from conlanger.tools.compile.asca._patterns import IPA_SEGMENT, SET_BODY_RE
from conlanger.tools.compile.asca.sets import (
    split_braced_set_members,
    split_set_members,
)
from conlanger.tools.compile.asca.structures import split_outside_groupers
from conlanger.tools.compile.field_tokens import (
    FieldToken,
    OptionalLengthNode,
    is_optional_length_token,
    is_set_token,
    token_to_raw_string,
)

_LENGTH = "\u02d0"
_CLASS_OR_TEMPLATE = r"[A-Z]\d*"
_MATRIX = r"[A-Z]:\[[^\]]+\]"
_SET = r"\{[^{}]*\}"

_SEGMENT_OPT_LEN_COMMA_RE = re.compile(rf"^({IPA_SEGMENT})\(({_LENGTH}),([^)]+)\)(.*)$")
_SEGMENT_OPT_LEN_RE = re.compile(rf"^({IPA_SEGMENT})\(({_LENGTH})\)(.*)$")
_CLASS_OPT_LEN_COMMA_RE = re.compile(
    rf"^({_CLASS_OR_TEMPLATE})\(({_LENGTH}),([^)]+)\)(.*)$"
)
_CLASS_OPT_LEN_RE = re.compile(rf"^({_CLASS_OR_TEMPLATE})\(({_LENGTH})\)(.*)$")
_MATRIX_OPT_LEN_RE = re.compile(rf"^({_MATRIX})\(({_LENGTH})\)(.*)$")
_SET_SUFFIX_OPT_LEN_RE = re.compile(rf"^({_SET})\(({_LENGTH})\)$")

_SEGMENT_OPT_LEN_COMMA_INLINE_RE = re.compile(
    rf"({IPA_SEGMENT})\(({_LENGTH}),([^)]+)\)"
)
_CLASS_OPT_LEN_COMMA_INLINE_RE = re.compile(
    rf"({_CLASS_OR_TEMPLATE})\(({_LENGTH}),([^)]+)\)"
)
_SET_SUFFIX_OPT_LEN_INLINE_RE = re.compile(rf"({_SET})\(({_LENGTH})\)")
_MATRIX_OPT_LEN_INLINE_RE = re.compile(rf"({_MATRIX})\(({_LENGTH})\)")
_CLASS_OPT_LEN_INLINE_RE = re.compile(
    rf"({_CLASS_OR_TEMPLATE})\(({_LENGTH})\)([^\s{{]*)"
)
_SEGMENT_OPT_LEN_INLINE_RE = re.compile(rf"({IPA_SEGMENT})\(({_LENGTH})\)([^\s{{]*)")


def _add_long_feature(segment: str) -> str:
    matrix_match = re.fullmatch(r"([A-Z]:\[[^\]]+\])(.*)", segment)
    if matrix_match:
        features, tail = matrix_match.groups()
        return f"{features[:-1]}, +long]{tail}"
    return f"{segment}:[+long]"


def _optional_length_members(node: OptionalLengthNode) -> tuple[str, ...]:
    short = f"{node.segment}{node.suffix}"
    long_form = f"{_add_long_feature(node.segment)}{node.suffix}"
    if node.comma_alt is None:
        return (short, long_form)
    alt_short = f"{node.segment}{node.comma_alt}{node.suffix}"
    alt_long = f"{_add_long_feature(node.segment)}{node.comma_alt}{node.suffix}"
    return (short, alt_short, long_form, alt_long)


def _set_optional_length_members(set_text: str) -> tuple[str, ...]:
    members = split_braced_set_members(set_text)
    short = "{" + ",".join(members) + "}"
    long_members = [_add_long_feature(member) for member in members]
    long_form = "{" + ",".join(long_members) + "}"
    return (short, long_form)


def parse_optional_length_part(part: str) -> FieldToken:
    """Parse one compile-field token; return ``OptionalLengthNode`` when matched."""
    for pattern, has_comma in (
        (_SEGMENT_OPT_LEN_COMMA_RE, True),
        (_CLASS_OPT_LEN_COMMA_RE, True),
        (_SEGMENT_OPT_LEN_RE, False),
        (_CLASS_OPT_LEN_RE, False),
        (_MATRIX_OPT_LEN_RE, False),
        (_SET_SUFFIX_OPT_LEN_RE, False),
    ):
        match = pattern.match(part)
        if not match:
            continue
        if has_comma:
            segment, _length, comma_alt, suffix = match.groups()
            return OptionalLengthNode(
                segment=segment,
                suffix=suffix,
                comma_alt=comma_alt,
            )
        groups = match.groups()
        if pattern is _SET_SUFFIX_OPT_LEN_RE:
            set_text, _length = groups
            return OptionalLengthNode(
                segment=set_text,
                suffix="",
                set_members=_set_optional_length_members(set_text),
            )
        segment, _length, suffix = groups
        return OptionalLengthNode(segment=segment, suffix=suffix)
    return part


def expand_optional_length_token(token: FieldToken) -> FieldToken:
    """Expand optional-length nodes to ordered brace-set field tokens."""
    if is_optional_length_token(token):
        if token.set_members is not None:
            return token.set_members
        return _optional_length_members(token)
    if is_set_token(token):
        expanded_members: list[str] = []
        for member in token:
            expanded = expand_optional_length_token(member)
            if is_set_token(expanded):
                expanded_members.extend(expanded)
            elif isinstance(expanded, str):
                expanded_members.append(expanded)
            else:
                expanded_members.extend(_optional_length_members(expanded))
        return tuple(expanded_members)
    return token


def expand_optional_length_tokens(
    tokens: tuple[FieldToken, ...],
) -> tuple[FieldToken, ...]:
    """Expand every optional-length node in a compile-field token tuple."""
    expanded: list[FieldToken] = []
    for token in tokens:
        result = expand_optional_length_token(token)
        expanded.append(result)
    return tuple(expanded)


def _render_optional_length_node(node: OptionalLengthNode) -> str:
    return token_to_raw_string(expand_optional_length_token(node))


def _expand_optional_length_member(member: str) -> str:
    def comma_repl(match: re.Match[str]) -> str:
        return _render_optional_length_node(
            OptionalLengthNode(
                segment=match.group(1),
                comma_alt=match.group(3),
            )
        )

    def set_repl(match: re.Match[str]) -> str:
        set_text = match.group(1)
        return _render_optional_length_node(
            OptionalLengthNode(
                segment=set_text,
                set_members=_set_optional_length_members(set_text),
            )
        )

    def suffix_repl(match: re.Match[str]) -> str:
        return _render_optional_length_node(
            OptionalLengthNode(segment=match.group(1), suffix=match.group(3) or "")
        )

    member = _SEGMENT_OPT_LEN_COMMA_INLINE_RE.sub(comma_repl, member)
    member = _CLASS_OPT_LEN_COMMA_INLINE_RE.sub(comma_repl, member)
    member = _SET_SUFFIX_OPT_LEN_INLINE_RE.sub(set_repl, member)
    member = _MATRIX_OPT_LEN_INLINE_RE.sub(
        lambda match: _render_optional_length_node(
            OptionalLengthNode(segment=match.group(1))
        ),
        member,
    )
    member = _CLASS_OPT_LEN_INLINE_RE.sub(suffix_repl, member)
    return _SEGMENT_OPT_LEN_INLINE_RE.sub(suffix_repl, member)


def _expand_sets_in_text(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        members = [
            _expand_optional_length_member(m) for m in split_set_members(match.group(1))
        ]
        return "{" + ",".join(members) + "}"

    return SET_BODY_RE.sub(repl, text)


def expand_optional_length_in_text(text: str) -> str:
    """Expand parenthesized optional-length notation in a compile-field string."""
    if not text or f"({_LENGTH}" not in text:
        return text
    text = _expand_sets_in_text(text)
    parts = split_outside_groupers(text)
    if not parts:
        return text
    expanded_parts = [_expand_optional_length_member(part) for part in parts]
    return " ".join(expanded_parts)
