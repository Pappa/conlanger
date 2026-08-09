"""Drop Index parallel-column null tokens before ASCA compile (ticket 60).

Index multi-segment rules may use ``∅``, ``*``, ``Ø``, or ``0`` as a parallel-column null alongside
other segments (e.g. ``c ɲ > ∅ n``). ASCA treats bare ``∅``/``*`` as pure
insertion/deletion only. When null tokens are mixed with other top-level segments,
omit the null columns so ASCA receives uneven-length substitution (``c ɲ > n``).

Pure deletion/insertion (``x > ∅``, ``∅ > x``) is unchanged. Null inside sets
(e.g. ``{j,∅}``) is not stripped — only space-separated top-level tokens.
"""

from __future__ import annotations

_NULL_COLUMN_TOKENS = frozenset({"∅", "Ø", "0", "*"})


def _split_outside_groupers(text: str, sep: str = " ") -> list[str]:
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


def _is_null_column_token(token: str) -> bool:
    return token in _NULL_COLUMN_TOKENS


def drop_mixed_parallel_null_columns(side: str) -> str:
    """Drop top-level ``∅``/``*`` tokens when mixed with other segments on one side."""
    if not side or not side.strip():
        return side
    tokens = _split_outside_groupers(side.strip())
    if not tokens:
        return side
    null_count = sum(1 for token in tokens if _is_null_column_token(token))
    if null_count == 0:
        return side
    if null_count == len(tokens):
        return side
    kept = [token for token in tokens if not _is_null_column_token(token)]
    return " ".join(kept)
