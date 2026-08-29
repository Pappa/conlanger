"""Tests for Index input-side optionals → ASCA structure optionals (ticket 51)."""

import re

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca import input_optionals as io
from conlanger.tools.compile.asca.input_optionals import (
    _expand_prefix_structure_optional,
    _is_structural_optional_inner,
    expand_input_optionals_to_structures,
)
from conlanger.tools.rules import DiachronicSeries


@pytest.mark.parametrize(
    ("index_rule", "expected"),
    [
        ("(V[-long])N", "{V[-long]}N"),
        ("(V:[+long])θt", "{V:[+long]}θt"),
        ("(C:[+labial])ɡ", "{C:[+labial]}ɡ"),
        ("(t:[+long])sn", "{t:[+long]}sn"),
        ("({C,#}V)ʔ", "{C,#,V}ʔ"),
        ("{s,z}(ʔ)", "{s,sʔ,z,zʔ}"),
        ("a{i,j}(a)", "a{i,j,a}"),
        ("{r,s}(N)k", "{rk,rNk,sk,sNk}"),
        (
            "{p,t,k}({p,t,k})n",
            "{pn,ppn,ptn,pkn,tn,tpn,ttn,tkn,kn,kpn,ktn,kkn}",
        ),
        ("V=0 3ʔ(0 )", "V=0 3ʔ{0}"),
        ("", ""),
        ("plain text", "plain text"),
        ("a{i}(i)", "a{i}"),
        ("({foo,bar})x", "{foo,bar}x"),
        ("({foo})x", "{foo}x"),
        ("( {foo} )x", "{foo}x"),
        ("{p,p}({p})n", "{pn,ppn}"),
        ("(notstructural)bar", "(notstructural)bar"),
        ("C > V / (C,V)_", "C > V / (C,V)_"),
        ("C > V / (C,0)_", "C > V / (C,0)_"),
    ],
)
def test_expand_input_optionals_to_structures(index_rule, expected):
    assert expand_input_optionals_to_structures(index_rule) == expected


@pytest.mark.parametrize(
    ("inp", "out", "env"),
    [
        ("(V[-long])N", "∅", "_#"),
        ("(V:[+long])θt", "{Vt:[+long],t:[+long]}", None),
        ("{s,z}(ʔ) {ʃ,ʒ}(ʔ) {ɬ,ɮ}(ʔ)", "s ʃ ɬ", "_#"),
        ("a{i,j}(a) a{u,w}", "e o", None),
        ("{r,s}(N)k", "k", "_V"),
        ("{r,s}pʰ {r,s}(N)p {r,s}b {r,s}mb", "pʰ p b mb", "_V"),
        (
            "(t:[+long])sn {kx,kxtx} rn ln",
            "s:[+long] x:[+long] r:[+long] l:[+long]",
            None,
        ),
        ("{p,t,k}({p,t,k})n {p,t,k}({p,t,k})m", "n:[+long] m:[+long]", None),
    ],
)
def test_input_optionals_inventory_representatives_validate(inp, out, env):
    rule = {"stages": [inp, out]}
    if env is not None:
        rule["env"] = env
    section = {"index": "1", "section": "input-opt", "rules": [rule]}
    validate_asca(DiachronicSeries(section, "asca"))


@pytest.mark.parametrize(
    ("inner", "expected"),
    [
        ("", False),
        ("C,V", False),
        ("V[-long]", True),
    ],
)
def test_is_structural_optional_inner(inner, expected):
    assert _is_structural_optional_inner(inner) is expected


def test_braced_prefix_wraps_unparsed_inner_without_brace_strip(monkeypatch):
    real_fullmatch = re.fullmatch

    def fake_fullmatch(pattern, string, *args, **kwargs):
        if pattern == r"\{([^{}]+)\}(.+)" and string == "{C}V":
            return None
        return real_fullmatch(pattern, string, *args, **kwargs)

    monkeypatch.setattr(io.re, "fullmatch", fake_fullmatch)
    assert _expand_prefix_structure_optional("({C}V)ʔ") == "{{C}V}ʔ"
