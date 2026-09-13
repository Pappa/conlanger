"""Cross-field env/exception feature-matrix compile transforms (ticket 131)."""

from __future__ import annotations

import re

from conlanger.tools.compile.asca._patterns import IPA_SEGMENT
from conlanger.tools.compile.asca.host_bracket_matrices import (
    _CLASS_HOST_BRACKET_RE,
    _IPA_HOST_BRACKET_RE,
    _SINGLE_HOST_BRACKET_RE,
)
from conlanger.tools.compile.asca.structures import split_outside_groupers

_BARE_MATRIX_RE = re.compile(r"^\[(?P<inner>[^\]]+)\]$")
_FEATURE_POLARITY_RE = re.compile(r"([+-])\s*([^,+-\]]+)")
_HOST_COLON_MATRIX_RE = re.compile(
    rf"^((?:[A-Z]|{IPA_SEGMENT})):(\[[^\]]+\])(?P<rest>.*)$"
)
_BARE_CLASS_LETTER_RE = re.compile(r"(?<![aeiou]C)([A-Z])")
_LENGTH_SUFFIX_RE = re.compile(r"^(?P<body>.+?)(?P<length>ː+)$")


def parse_bare_feature_matrix(text: str | None) -> str | None:
    """Return the matrix when ``text`` is a standalone ``[±feature]`` field."""
    if not text:
        return None
    match = _BARE_MATRIX_RE.fullmatch(text.strip())
    if match is None:
        return None
    return match.group(0)


def flip_feature_matrix_polarity(matrix: str) -> str:
    """Flip ``+``/``-`` on each feature inside a standalone matrix."""
    if not matrix.startswith("[") or not matrix.endswith("]"):
        return matrix

    def flip(match: re.Match[str]) -> str:
        sign = match.group(1)
        name = match.group(2)
        flipped = "-" if sign == "+" else "+"
        return f"{flipped}{name}"

    inner = _FEATURE_POLARITY_RE.sub(flip, matrix[1:-1])
    return f"[{inner}]"


def _merge_feature_matrix_inners(inner_a: str, inner_b: str) -> str:
    left = inner_a.strip().rstrip(",")
    right = inner_b.strip()
    if not left:
        return right
    if not right:
        return left
    return f"{left}, {right}"


def _attach_matrix_to_literal_segment(text: str, matrix: str) -> str | None:
    if re.fullmatch(r"[A-Z]", text):
        return f"{text}{matrix}"

    if _BARE_CLASS_LETTER_RE.search(text):
        return None

    length_match = _LENGTH_SUFFIX_RE.match(text)
    if length_match is not None:
        body = length_match.group("body")
        if re.fullmatch(IPA_SEGMENT, body):
            return f"{body}{matrix}{length_match.group('length')}"

    if re.fullmatch(IPA_SEGMENT, text):
        return f"{text}{matrix}"

    return None


def _attach_matrix_to_token(token: str, matrix: str) -> str:
    text = token.strip()
    if not text:
        return token
    matrix_inner = matrix[1:-1]

    host_bracket = _SINGLE_HOST_BRACKET_RE.fullmatch(text)
    if host_bracket is not None:
        host = host_bracket.group(1)
        merged = _merge_feature_matrix_inners(host_bracket.group(2), matrix_inner)
        return f"{host}[{merged}]"

    host_colon = _HOST_COLON_MATRIX_RE.match(text)
    if host_colon is not None:
        host = host_colon.group(1)
        existing_inner = host_colon.group(2)[1:-1]
        merged = _merge_feature_matrix_inners(existing_inner, matrix_inner)
        return f"{host}:[{merged}]{host_colon.group('rest')}"

    literal = _attach_matrix_to_literal_segment(text, matrix)
    if literal is not None:
        return literal

    if text.startswith("{") and text.endswith("}"):
        members = split_outside_groupers(text[1:-1], ",")
        transformed = ",".join(
            _attach_matrix_to_token(member.strip(), matrix) for member in members
        )
        return f"{{{transformed}}}"

    def class_repl(match: re.Match[str]) -> str:
        host = match.group("host")
        merged = _merge_feature_matrix_inners(match.group("matrix"), matrix_inner)
        return f"{host}[{merged}]"

    if _CLASS_HOST_BRACKET_RE.search(text):
        return _CLASS_HOST_BRACKET_RE.sub(class_repl, text, count=1)

    def ipa_repl(match: re.Match[str]) -> str:
        host = match.group("host")
        if re.search(r"[A-Z]", host):
            return match.group(0)
        merged = _merge_feature_matrix_inners(match.group("matrix"), matrix_inner)
        return f"{host}[{merged}]"

    if _IPA_HOST_BRACKET_RE.search(text):
        return _IPA_HOST_BRACKET_RE.sub(ipa_repl, text, count=1)

    bare_class = _BARE_CLASS_LETTER_RE.search(text)
    if bare_class is not None:
        insert_at = bare_class.end()
        return f"{text[:insert_at]}{matrix}{text[insert_at:]}"

    return token


def apply_segment_at_focus_matrix_to_input(input_text: str, matrix: str) -> str:
    """Attach a segment-at-focus feature matrix to compiled input tokens."""
    if not input_text or not matrix:
        return input_text
    columns = split_outside_groupers(input_text, " ")
    return " ".join(_attach_matrix_to_token(column, matrix) for column in columns)


def resolve_bare_env_exception_feature_matrices(
    inp: str,
    output: str,
    env: str | None,
    exception: str | None,
    *,
    env_raw: str | None = None,
    exception_raw: str | None = None,
) -> tuple[str, str, str | None, str | None]:
    """Rewrite bare env/exception matrices onto input (Families A and B)."""
    bare_env = parse_bare_feature_matrix(env_raw if env_raw is not None else env)
    bare_exception = parse_bare_feature_matrix(
        exception_raw if exception_raw is not None else exception
    )

    if bare_env is not None:
        inp = apply_segment_at_focus_matrix_to_input(inp, bare_env)
        env = "_"

    if bare_exception is not None:
        inp = apply_segment_at_focus_matrix_to_input(
            inp,
            flip_feature_matrix_polarity(bare_exception),
        )
        exception = None

    return inp, output, env, exception
