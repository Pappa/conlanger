"""Tests for compile-time parallel-column null stripping (ticket 60)."""

import pytest

from conlanger.tools.compile.asca.parallel_null_columns import (
    drop_mixed_parallel_null_columns,
)


@pytest.mark.parametrize(
    ("side", "expected"),
    [
        ("c ɲ", "c ɲ"),
        ("∅ n", "n"),
        ("∅ ʃ", "ʃ"),
        ("k ʃ", "k ʃ"),
        ("∅", "∅"),
        ("*", "*"),
        ("x", "x"),
        ("k c > ∅ {j,∅}", "k c > {j,∅}"),  # only top-level ∅ dropped when used as I/O
    ],
)
def test_drop_mixed_parallel_null_columns_side(side, expected):
    if " > " in side:
        inp, out = side.split(" > ", 1)
        assert (
            drop_mixed_parallel_null_columns(inp)
            + " > "
            + drop_mixed_parallel_null_columns(out)
            == expected
        )
    else:
        assert drop_mixed_parallel_null_columns(side) == expected


def test_drop_mixed_parallel_null_columns_proto_star_token_unchanged():
    assert drop_mixed_parallel_null_columns("*T") == "*T"
    assert drop_mixed_parallel_null_columns("*L") == "*L"
