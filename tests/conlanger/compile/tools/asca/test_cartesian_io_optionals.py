"""Tests for cartesian I/O optional flatten (ticket 111)."""

import pytest

from conlanger.compile.tools.asca.cartesian_io_optionals import (
    _bases_are_modifier_variants,
    _find_matching_close,
    _find_matching_open,
    _rewrite_nested_set_members,
    _split_trailing_set,
    flatten_cartesian_io_optionals,
)
from conlanger.compile.tools.asca.planned import expand_meta_notation


@pytest.mark.parametrize(
    ("after_parenthetical", "expected"),
    [
        ("{hə{p,b},ə{p,b}}", "{həp,həb,əp,əb}"),
        ("{j{u,ʌ},{u,ʌ}}", "{ju,jʌ,u,ʌ}"),
        ("{e{V[- low]},eC{V[- low]}}", "{eV[- low],eCV[- low]}"),
        ("{k{r,j},kʰ{r,j}}", "{k,kʰ}{r,j}"),
        ("{ɡ{r,j},ɡʷ{r,j}}", "{ɡ,ɡʷ}{r,j}"),
        ("{GV,V}", "{GV,V}"),
        ("{ɡ,ɡʷ}", "{ɡ,ɡʷ}"),
        ("plain text", "plain text"),
        ("", ""),
    ],
)
def test_flatten_cartesian_io_optionals(after_parenthetical, expected):
    assert flatten_cartesian_io_optionals(after_parenthetical) == expected


def test_find_matching_close_rejects_invalid_open_index():
    assert _find_matching_close("text", 0) is None
    assert _find_matching_close("{a", 0) is None


def test_find_matching_open_returns_none_for_unbalanced_member():
    assert _find_matching_open("a{b", 2) is None
    assert _split_trailing_set("a{b") is None


def test_bases_are_modifier_variants_rejects_optional_prefix_shapes():
    assert _bases_are_modifier_variants(["j", ""]) is False
    assert _bases_are_modifier_variants(["k", "kʰ"]) is True


def test_rewrite_nested_set_members_rejects_mismatched_inners():
    assert _rewrite_nested_set_members("a{x},b{y}") is None
    assert _rewrite_nested_set_members("") is None


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("{a,b}", "{a,b}"),
        ("{a{x},b{y}}", "{a{x},b{y}}"),
        ("unbalanced {", "unbalanced {"),
    ],
)
def test_flatten_cartesian_io_optionals_edge_cases(text, expected):
    assert flatten_cartesian_io_optionals(text) == expected


@pytest.mark.parametrize(
    ("index_rule", "expected"),
    [
        ("(h)ə{p,b}", "{həp,həb,əp,əb}"),
        ("(j){u,ʌ}", "{ju,jʌ,u,ʌ}"),
        ("k(ʰ){r,j}", "{k,kʰ}{r,j}"),
        ("(G)V", "{GV,V}"),
        ("ɡ(ʷ)", "{ɡ,ɡʷ}"),
        ("{s,z}(ʔ)", "{s,sʔ,z,zʔ}"),
        ("{r,s}(N)k", "{rk,rNk,sk,sNk}"),
        ("a{i,j}(a)", "a{i,j,ia,ja}"),
        ("(V[-long])N", "{V:[-long]N,N}"),
        ("({C,#}V)ʔ", "({C,#}V)ʔ"),
    ],
)
def test_expand_meta_notation_cartesian_io(index_rule, expected):
    assert expand_meta_notation(index_rule) == expected
