"""Tests for cartesian I/O optional flatten (ticket 111)."""

import shutil
from pathlib import Path

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.cartesian_io_optionals import (
    _bases_are_modifier_variants,
    _find_matching_close,
    _find_matching_open,
    _rewrite_nested_set_members,
    _split_trailing_set,
    flatten_cartesian_io_optionals,
)
from conlanger.tools.compile.asca.planned import expand_meta_notation
from conlanger.tools.rules import DiachronicSeries


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
        ("(V[-long])N", "(V[-long])N"),
        ("({C,#}V)ʔ", "({C,#}V)ʔ"),
    ],
)
def test_expand_meta_notation_cartesian_io(index_rule, expected):
    assert expand_meta_notation(index_rule) == expected


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_muong_khen_apply_probe(tmp_path: Path):
    probe = tmp_path / "probe.wsca"
    probe.write_text("həpl\n", encoding="utf-8")
    section = {
        "index": "Muong-Khen",
        "section": "Proto-Vietic to Muong Khen",
        "rules": [{"stages": ["(h)ə{p,b}", "t"], "env": "_l"}],
    }
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_scots_output_apply_probe(tmp_path: Path):
    probe = tmp_path / "probe.wsca"
    probe.write_text("øː\n", encoding="utf-8")
    section = {
        "index": "Scots",
        "section": "Old English to Scots",
        "rules": [
            {
                "stages": ["øː", "(j){u,ʌ}"],
                "env": "_{k,x}",
            }
        ],
    }
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_naxi_set_class_optional_apply_probe(tmp_path: Path):
    probe = tmp_path / "probe.wsca"
    probe.write_text("rk\nsk\n", encoding="utf-8")
    section = {
        "index": "Naxi",
        "section": "Naxi",
        "rules": [{"stages": ["{r,s}(N)k", "k"], "env": "_V"}],
    }
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_amdo_modifier_adjacent_sets_apply_probe(tmp_path: Path):
    probe = tmp_path / "probe.wsca"
    probe.write_text("kr\n", encoding="utf-8")
    section = {
        "index": "Amdo",
        "section": "Old Tibetan to Amdo dialects",
        "rules": [{"stages": ["k(ʰ){r,j}", "tɕ"]}],
    }
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)
