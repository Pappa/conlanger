"""Parallel-column null handling for ASCA compile (tickets 60 and 81).

Index multi-segment rules may use ``∅``, ``*``, ``Ø``, or ``0`` as a parallel-column null alongside
other segments (e.g. ``c ɲ > ∅ n``). ASCA treats bare ``∅``/``*`` as pure
insertion/deletion only. When null tokens are mixed with other top-level segments,
omit the null columns so ASCA receives uneven-length substitution (``c ɲ > n``).

Index also writes paired parallel outputs with deletion branches inline, e.g.
``{r,h} > {∅,h}`` or ``{m,ɲ} n > {ɲ,∅} {ŋ,∅}``. ASCA accepts ``∅`` as a
segment but not inside correspondence sets. This module zips parallel columns
into concrete input/output pairs (one branch per alternative index) so
``SoundChangeRule`` can emit peer alternatives for inventory validation.

Pure deletion/insertion (``x > ∅``, ``∅ > x``) is unchanged. Null inside sets
(e.g. ``{j,∅}``) is not stripped — only space-separated top-level tokens.

Whole-field unpaired optional outputs (``d > {∅,ð}``) remain ticket 66.
"""

from __future__ import annotations

from conlanger.tools.compile.asca.sets import (
    is_whole_field_set,
    split_braced_set_members,
)
from conlanger.tools.compile.asca.structures import split_outside_groupers

_NULL_TOKENS = frozenset({"∅", "Ø", "0", "*"})


def _is_null_column_token(token: str) -> bool:
    return token in _NULL_TOKENS


def drop_mixed_parallel_null_columns(side: str) -> str:
    """Drop top-level ``∅``/``*`` tokens when mixed with other segments on one side."""
    if not side or not side.strip():
        return side
    tokens = split_outside_groupers(side.strip())
    if not tokens:
        return side
    null_count = sum(1 for token in tokens if _is_null_column_token(token))
    if null_count == 0:
        return side
    if null_count == len(tokens):
        return side
    kept = [token for token in tokens if not _is_null_column_token(token)]
    return " ".join(kept)


def _set_contains_null_member(token: str) -> bool:
    if not is_whole_field_set(token):
        return False
    return any(member in _NULL_TOKENS for member in split_braced_set_members(token))


def _output_contains_null_in_set(output: str) -> bool:
    if not output or not output.strip():
        return False
    if is_whole_field_set(output.strip()) and _set_contains_null_member(output):
        return True
    return any(
        _set_contains_null_member(token) for token in split_outside_groupers(output)
    )


def _column_branch_pairs(
    input_col: str, output_col: str
) -> list[tuple[str, str]] | None:
    in_members = (
        split_braced_set_members(input_col)
        if is_whole_field_set(input_col)
        else [input_col.strip()]
    )
    out_members = (
        split_braced_set_members(output_col)
        if is_whole_field_set(output_col)
        else [output_col.strip()]
    )
    if not in_members or not out_members:
        return None
    if any(not member or "{" in member for member in in_members + out_members):
        return None
    if len(in_members) == len(out_members):
        return list(zip(in_members, out_members, strict=True))
    if len(in_members) == 1:
        return [(in_members[0], out_member) for out_member in out_members]
    if len(out_members) == 1:
        return [(in_member, out_members[0]) for in_member in in_members]
    return None


def _finalize_branch_io(input_text: str, output_text: str) -> tuple[str, str]:
    input_text = drop_mixed_parallel_null_columns(input_text)
    output_text = drop_mixed_parallel_null_columns(output_text)
    out_tokens = split_outside_groupers(output_text.strip())
    if out_tokens and all(token in _NULL_TOKENS for token in out_tokens):
        output_text = "∅"
    return input_text, output_text


def _expand_uneven_input_set_to_output_set(
    input_cols: list[str], output_cols: list[str]
) -> list[tuple[str, str]] | None:
    """``{b,k} r > {r,∅}`` — input set + trailing segment, single output set."""
    if len(input_cols) != 2 or len(output_cols) != 1:
        return None
    if not is_whole_field_set(input_cols[0]) or not is_whole_field_set(output_cols[0]):
        return None
    pairs = _column_branch_pairs(input_cols[0], output_cols[0])
    if pairs is None:
        return None
    trailing_input = input_cols[1].strip()
    branches: list[tuple[str, str]] = []
    for in_member, out_member in pairs:
        input_branch = f"{in_member} {trailing_input}"
        if out_member in _NULL_TOKENS:
            output_branch = "∅"
        else:
            output_branch = out_member
        branches.append(_finalize_branch_io(input_branch, output_branch))
    return branches


def expand_parallel_output_null_branches(
    input_text: str, output_text: str
) -> list[tuple[str, str]] | None:
    """Return zipped branch ``(input, output)`` pairs when output sets contain ``∅``.

    Returns ``None`` when the rule is out of scope or cannot be expanded uniformly.
    """
    if not _output_contains_null_in_set(output_text):
        return None

    input_cols = split_outside_groupers(input_text.strip())
    output_cols = split_outside_groupers(output_text.strip())
    if not input_cols or not output_cols:
        return None

    # Whole-field unpaired optional outputs are handled in ``SoundChangeRule`` (ticket 66).
    if (
        len(input_cols) == 1
        and not is_whole_field_set(input_text)
        and is_whole_field_set(output_text)
    ):
        return None

    if len(input_cols) != len(output_cols):
        uneven = _expand_uneven_input_set_to_output_set(input_cols, output_cols)
        if uneven is not None:
            return uneven
        return None

    column_pairs: list[list[tuple[str, str]]] = []
    for input_col, output_col in zip(input_cols, output_cols, strict=True):
        pairs = _column_branch_pairs(input_col, output_col)
        if pairs is None:
            return None
        column_pairs.append(pairs)

    branch_count = max(len(pairs) for pairs in column_pairs)
    for pairs in column_pairs:
        if len(pairs) != 1 and len(pairs) != branch_count:
            return None

    branches: list[tuple[str, str]] = []
    for branch_idx in range(branch_count):
        in_parts: list[str] = []
        out_parts: list[str] = []
        for pairs in column_pairs:
            pair = pairs[branch_idx] if len(pairs) == branch_count else pairs[0]
            in_parts.append(pair[0])
            out_parts.append(pair[1])
        finalized = _finalize_branch_io(" ".join(in_parts), " ".join(out_parts))
        branches.append(finalized)
    return branches
