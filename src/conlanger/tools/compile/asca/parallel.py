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

from conlanger.tools.compile.field_tokens import (
    FieldToken,
    is_set_token,
    is_whole_field_set_tokens,
    parse_field_tokens,
    render_field_tokens,
    set_contains_null_member,
    token_to_raw_string,
)

_NULL_TOKENS = frozenset({"∅", "Ø", "0", "*"})


def _is_null_column_token(token: str) -> bool:
    return token in _NULL_TOKENS


def drop_mixed_parallel_null_columns_tokens(
    tokens: tuple[FieldToken, ...],
) -> tuple[FieldToken, ...]:
    """Drop singleton null field tokens when mixed with other parallel tokens."""
    if not tokens:
        return tokens
    null_count = sum(
        1 for token in tokens if isinstance(token, str) and _is_null_column_token(token)
    )
    if null_count == 0 or null_count == len(tokens):
        return tokens
    return tuple(
        token
        for token in tokens
        if not (isinstance(token, str) and _is_null_column_token(token))
    )


def drop_mixed_parallel_null_columns(side: str) -> str:
    """Drop top-level ``∅``/``*`` tokens when mixed with other segments on one side."""
    if not side or not side.strip():
        return side
    tokens = parse_field_tokens(side.strip())
    if not tokens:
        return side
    dropped = drop_mixed_parallel_null_columns_tokens(tokens)
    return render_field_tokens(dropped)


def _output_tokens_contain_null_in_set(output_tokens: tuple[FieldToken, ...]) -> bool:
    if not output_tokens:
        return False
    if is_whole_field_set_tokens(output_tokens) and set_contains_null_member(
        output_tokens[0]
    ):
        return True
    return any(set_contains_null_member(token) for token in output_tokens)


def _column_branch_pairs_tokens(
    input_col: FieldToken, output_col: FieldToken
) -> list[tuple[str, str]] | None:
    in_members = (
        list(input_col)
        if is_set_token(input_col)
        else [token_to_raw_string(input_col).strip()]
    )
    out_members = (
        list(output_col)
        if is_set_token(output_col)
        else [token_to_raw_string(output_col).strip()]
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


def _column_branch_pairs(
    input_col: str, output_col: str
) -> list[tuple[str, str]] | None:
    input_tokens = parse_field_tokens(input_col.strip())
    output_tokens = parse_field_tokens(output_col.strip())
    if not input_tokens or not output_tokens:
        return None
    return _column_branch_pairs_tokens(input_tokens[0], output_tokens[0])


def _finalize_branch_io_tokens(
    input_tokens: tuple[FieldToken, ...],
    output_tokens: tuple[FieldToken, ...],
) -> tuple[tuple[FieldToken, ...], tuple[FieldToken, ...]]:
    input_tokens = drop_mixed_parallel_null_columns_tokens(input_tokens)
    output_tokens = drop_mixed_parallel_null_columns_tokens(output_tokens)
    if output_tokens and all(
        isinstance(token, str) and token in _NULL_TOKENS for token in output_tokens
    ):
        return input_tokens, ("∅",)
    return input_tokens, output_tokens


def _expand_uneven_input_set_to_output_set_tokens(
    input_cols: tuple[FieldToken, ...],
    output_cols: tuple[FieldToken, ...],
) -> list[tuple[tuple[FieldToken, ...], tuple[FieldToken, ...]]] | None:
    if len(input_cols) != 2 or len(output_cols) != 1:
        return None
    if not is_set_token(input_cols[0]) or not is_set_token(output_cols[0]):
        return None
    pairs = _column_branch_pairs_tokens(input_cols[0], output_cols[0])
    if pairs is None:
        return None
    trailing_input = token_to_raw_string(input_cols[1]).strip()
    branches: list[tuple[tuple[FieldToken, ...], tuple[FieldToken, ...]]] = []
    for in_member, out_member in pairs:
        input_branch = parse_field_tokens(f"{in_member} {trailing_input}")
        if out_member in _NULL_TOKENS:
            output_branch: tuple[FieldToken, ...] = ("∅",)
        else:
            output_branch = parse_field_tokens(out_member)
        branches.append(_finalize_branch_io_tokens(input_branch, output_branch))
    return branches


def expand_parallel_output_null_branches_from_tokens(
    input_tokens: tuple[FieldToken, ...],
    output_tokens: tuple[FieldToken, ...],
) -> list[tuple[tuple[FieldToken, ...], tuple[FieldToken, ...]]] | None:
    """Return zipped branch token pairs when output sets contain ``∅``."""
    if not _output_tokens_contain_null_in_set(output_tokens):
        return None
    if not input_tokens or not output_tokens:
        return None

    # Whole-field unpaired optional outputs are handled in ``SoundChangeRule`` (ticket 66).
    if (
        len(input_tokens) == 1
        and not is_set_token(input_tokens[0])
        and len(output_tokens) == 1
        and is_set_token(output_tokens[0])
    ):
        return None

    if len(input_tokens) != len(output_tokens):
        uneven = _expand_uneven_input_set_to_output_set_tokens(
            input_tokens, output_tokens
        )
        if uneven is not None:
            return uneven
        return None

    column_pairs: list[list[tuple[str, str]]] = []
    for input_col, output_col in zip(input_tokens, output_tokens, strict=True):
        pairs = _column_branch_pairs_tokens(input_col, output_col)
        if pairs is None:
            return None
        column_pairs.append(pairs)

    branch_count = max(len(pairs) for pairs in column_pairs)
    for pairs in column_pairs:
        if len(pairs) != 1 and len(pairs) != branch_count:
            return None

    branches: list[tuple[tuple[FieldToken, ...], tuple[FieldToken, ...]]] = []
    for branch_idx in range(branch_count):
        in_parts: list[str] = []
        out_parts: list[str] = []
        for pairs in column_pairs:
            pair = pairs[branch_idx] if len(pairs) == branch_count else pairs[0]
            in_parts.append(pair[0])
            out_parts.append(pair[1])
        finalized = _finalize_branch_io_tokens(
            parse_field_tokens(" ".join(in_parts)),
            parse_field_tokens(" ".join(out_parts)),
        )
        branches.append(finalized)
    return branches


def expand_parallel_output_null_branches(
    input_text: str, output_text: str
) -> list[tuple[str, str]] | None:
    """Return zipped branch ``(input, output)`` pairs when output sets contain ``∅``.

    Returns ``None`` when the rule is out of scope or cannot be expanded uniformly.
    """
    branches = expand_parallel_output_null_branches_from_tokens(
        parse_field_tokens(input_text.strip()),
        parse_field_tokens(output_text.strip()),
    )
    if branches is None:
        return None
    return [
        (render_field_tokens(input_tokens), render_field_tokens(output_tokens))
        for input_tokens, output_tokens in branches
    ]
