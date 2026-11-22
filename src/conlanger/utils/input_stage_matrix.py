"""Attach segment-at-focus feature matrices to Index rule input stages (parse tier)."""

from __future__ import annotations

import re

_POSTFIX_MATRIX_RE = re.compile(r"^(?P<host>.+?)(?P<mtx>\[[^\]]+\])$")
_COLON_MATRIX_RE = re.compile(r"^(?P<host>.+?):\[(?P<inner>[^\]]+)\](?P<rest>.*)$")


def _merge_matrix_inners(inner_a: str, inner_b: str) -> str:
    left = inner_a.strip().rstrip(",")
    right = inner_b.strip()
    if not left:
        return right
    if not right:
        return left
    return f"{left}, {right}"


def attach_focus_matrix_to_input_stage(
    stages: list[str], matrix: str
) -> list[str] | None:
    """Merge ``[±feature]`` onto the first input stage (postfix, colon, or bare host)."""
    if not stages or not matrix:
        return None
    input_stage = stages[0].strip()
    if not input_stage:
        return None

    matrix_inner = matrix[1:-1]

    colon_match = _COLON_MATRIX_RE.match(input_stage)
    if colon_match is not None:
        merged = _merge_matrix_inners(colon_match.group("inner"), matrix_inner)
        host = colon_match.group("host")
        rest = colon_match.group("rest")
        return [f"{host}:[{merged}]{rest}", *stages[1:]]

    postfix_match = _POSTFIX_MATRIX_RE.match(input_stage)
    if postfix_match is not None:
        existing_inner = postfix_match.group("mtx")[1:-1]
        merged = _merge_matrix_inners(existing_inner, matrix_inner)
        host = postfix_match.group("host")
        return [f"{host}[{merged}]", *stages[1:]]

    if ":" in input_stage or "[" in input_stage:
        return None
    if " " in input_stage or "{" in input_stage:
        return None

    return [f"{input_stage}:{matrix}", *stages[1:]]
