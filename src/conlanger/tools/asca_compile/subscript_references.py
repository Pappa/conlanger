"""Compile-time expansion of Index positional slots and identity subscripts."""

from __future__ import annotations

import re

from conlanger.tools.series_mappings import (
    is_identity_subscript_token,
    is_positional_slot_token,
)

_SUBSCRIPT_TO_ASCII = str.maketrans("₁₂₃₄₅₆₇₈₉", "123456789")
_SUBSCRIPT_CHAR_RE = re.compile(r"[₀₁₂₃₄₅₆₇₈₉]")
_POSITIONAL_RE = re.compile(r"([A-Z])([₁₂₃₄₅₆₇₈₉])")
_IDENTITY_RE = re.compile(r"([A-Za-z])₀")
_MATRIX_ATTACHED_IDENTITY_RE = re.compile(r"([A-Za-z])₀(\[[^\]]+\])")


def _split_rule_fields(text: str) -> tuple[str, str, str | None, str | None]:
    exception: str | None = None
    if " // " in text:
        text, exception = text.split(" // ", 1)
    env: str | None = None
    if " > " in text:
        inp, rest = text.split(" > ", 1)
        if " / " in rest:
            output, env = rest.split(" / ", 1)
        else:
            output = rest
    else:
        inp = text
        output = ""
    return inp, output, env, exception


def _join_rule_fields(
    inp: str,
    output: str,
    env: str | None,
    exception: str | None,
) -> str:
    result = f"{inp} > {output}"
    if env:
        result += f" / {env}"
    if exception:
        result += f" // {exception}"
    return result


def _normalize_field_spacing(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _expand_field_segment(segment: str, declared: set[int]) -> str:
    def replace_positional(match: re.Match[str]) -> str:
        base = match.group(1)
        digit = int(match.group(2).translate(_SUBSCRIPT_TO_ASCII))
        if digit not in declared:
            declared.add(digit)
            return f"{base}={digit} "
        return f"{digit} "

    def replace_identity(match: re.Match[str]) -> str:
        base = match.group(1)
        if 0 not in declared:
            declared.add(0)
            return f"{base}=0 "
        return "0 "

    expanded = _POSITIONAL_RE.sub(replace_positional, segment)
    expanded = _IDENTITY_RE.sub(replace_identity, expanded)
    return _normalize_field_spacing(expanded)


def _expand_field(text: str, declared: set[int]) -> str:
    if not text:
        return text
    parts: list[str] = []
    for segment in re.split(r"(\[[^\]]*\])", text):
        if not segment:
            continue
        if segment.startswith("[") and segment.endswith("]"):
            parts.append(segment)
        else:
            parts.append(_expand_field_segment(segment, declared))
    return _normalize_field_spacing("".join(parts))


def expand_index_subscript_references(text: str) -> str:
    """Map positional slots and identity subscripts to ASCA reference syntax."""
    if not text or not _SUBSCRIPT_CHAR_RE.search(text):
        return text

    inp, output, env, exception = _split_rule_fields(text)
    declared: set[int] = set()

    inp = _expand_field(inp, declared)
    output = _expand_field(output, declared)

    if env is not None:
        original_env = env
        env = _expand_field(env, declared)
        if env != original_env and "_" not in env:
            env = f"_ {env}"

    if exception is not None:
        exception = _expand_field(exception, declared)

    return _join_rule_fields(inp, output, env, exception)


def is_easy_subscript_rule_text(text: str) -> bool:
    """Whether ``text`` is in scope for phase-1 positional/identity expansion."""
    if _MATRIX_ATTACHED_IDENTITY_RE.search(text):
        return False
    if "ˤ" in text:
        return False
    for token in re.findall(r"\S+", text):
        if is_positional_slot_token(token) or is_identity_subscript_token(token):
            continue
        if _SUBSCRIPT_CHAR_RE.search(token):
            return False
    return bool(_SUBSCRIPT_CHAR_RE.search(text))
