"""Tests for parallel output set ∅ expansion (ticket 81)."""

import pytest

from conlanger.tools.compile.asca.parallel_output_null import (
    expand_parallel_output_null_branches,
)


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
    ("input_text", "output_text"),
    [
        ("k b r", "{ŋ,∅} {w,m} {n,r,t}"),  # uneven branch counts across columns
        ("d", "{∅,ð}"),  # optional-output shape — expander returns None
        ("c ɲ", "∅ n"),  # top-level column null — ticket 60
    ],
)
def test_expand_parallel_output_null_branches_out_of_scope(input_text, output_text):
    assert expand_parallel_output_null_branches(input_text, output_text) is None
