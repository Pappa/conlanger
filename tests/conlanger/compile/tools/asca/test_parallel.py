"""Tests for parallel-column null handling at ASCA compile time (tickets 60 and 81)."""

import pytest

from conlanger.tools.compile.asca.parallel import (
    _column_branch_pairs,
    drop_mixed_parallel_null_columns,
    expand_parallel_output_null_branches,
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


@pytest.mark.parametrize(
    ("input_text", "output_text", "expected_branches"),
    [
        ("{r,h}", "{∅,h}", [("r", "∅"), ("h", "h")]),
        ("{pʰ,ŋ}", "{∅,j}", [("pʰ", "∅"), ("ŋ", "j")]),
        ("{m,ɲ} n", "{ɲ,∅} {ŋ,∅}", [("m n", "ɲ ŋ"), ("ɲ n", "∅")]),
        ("m l", "{m,n} {l,∅}", [("m l", "m l"), ("m l", "n")]),
        ("p k", "ɸ {∅,k}", [("p k", "ɸ"), ("p k", "ɸ k")]),
        ("{tʰ,d} {k,ɡ}", "r {h,∅}", [("tʰ k", "r h"), ("d ɡ", "r")]),
        ("{b,k} r", "{r,∅}", [("b r", "r"), ("k r", "∅")]),
        (
            "k b r",
            "{ŋ,∅} {w,m} {n,r,t}",
            [
                ("k b r", "ŋ w n"),
                ("k b r", "ŋ w r"),
                ("k b r", "ŋ w t"),
                ("k b r", "ŋ m n"),
                ("k b r", "ŋ m r"),
                ("k b r", "ŋ m t"),
                ("k b r", "w n"),
                ("k b r", "w r"),
                ("k b r", "w t"),
                ("k b r", "m n"),
                ("k b r", "m r"),
                ("k b r", "m t"),
            ],
        ),
        (
            "b d k",
            "{b,β} {ɾ,∅} {k,x,ɡ,ɣ}",
            [
                ("b d k", "b ɾ k"),
                ("b d k", "b ɾ x"),
                ("b d k", "b ɾ ɡ"),
                ("b d k", "b ɾ ɣ"),
                ("b d k", "b k"),
                ("b d k", "b x"),
                ("b d k", "b ɡ"),
                ("b d k", "b ɣ"),
                ("b d k", "β ɾ k"),
                ("b d k", "β ɾ x"),
                ("b d k", "β ɾ ɡ"),
                ("b d k", "β ɾ ɣ"),
                ("b d k", "β k"),
                ("b d k", "β x"),
                ("b d k", "β ɡ"),
                ("b d k", "β ɣ"),
            ],
        ),
        (
            "m n h j",
            "b {n,r,∅} {h,∅} {j,∅}",
            [
                ("m n h j", "b n h j"),
                ("m n h j", "b n h"),
                ("m n h j", "b n j"),
                ("m n h j", "b n"),
                ("m n h j", "b r h j"),
                ("m n h j", "b r h"),
                ("m n h j", "b r j"),
                ("m n h j", "b r"),
                ("m n h j", "b h j"),
                ("m n h j", "b h"),
                ("m n h j", "b j"),
                ("m n h j", "b"),
            ],
        ),
    ],
)
def test_expand_parallel_output_null_branches(
    input_text, output_text, expected_branches
):
    assert (
        expand_parallel_output_null_branches(input_text, output_text)
        == expected_branches
    )


@pytest.mark.parametrize(
    ("input_text", "output_text", "expected_count"),
    [
        ("b d k", "{b,β} {ɾ,l,∅} {k,x,ɡ,ɣ}", 24),
    ],
)
def test_expand_parallel_output_null_branches_uneven_width_counts(
    input_text, output_text, expected_count
):
    branches = expand_parallel_output_null_branches(input_text, output_text)
    assert branches is not None
    assert len(branches) == expected_count


@pytest.mark.parametrize(
    ("input_text", "output_text"),
    [
        ("d", "{∅,ð}"),  # optional-output shape — expander returns None
        ("c ɲ", "∅ n"),  # top-level column null — ticket 60
        ("", "{∅,a}"),  # empty input columns after split
        ("{a,b} x y", "{r,∅}"),  # uneven column count with no uneven-set expansion
        ("{a,b,c} x", "{x,y} {∅,a}"),  # mismatched correspondence set widths
        ("{a,{b,c}}", "{∅,x,y}"),  # nested set members are not expandable
    ],
)
def test_expand_parallel_output_null_branches_out_of_scope(input_text, output_text):
    assert expand_parallel_output_null_branches(input_text, output_text) is None


@pytest.mark.parametrize(
    ("input_col", "output_col"),
    [
        ("{a,b,c}", "{x,y}"),
        ("{,}", "{∅,a}"),
    ],
)
def test_column_branch_pairs_rejects_non_uniform_set_widths(input_col, output_col):
    assert _column_branch_pairs(input_col, output_col) is None
