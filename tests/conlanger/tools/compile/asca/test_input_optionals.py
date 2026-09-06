"""Tests for Index input-side optionals → ASCA structure optionals (ticket 51)."""

import re
import shutil
from pathlib import Path

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
        ("(V:[+long])θt", "{V:[+long]θt,θt}"),
        ("(C:[+labial])ɡ", "{C:[+labial]ɡ,ɡ}"),
        ("(t:[+long])sn", "{t:[+long]sn,sn}"),
        ("(V[-long])N", "{V:[-long]N,N}"),
        ("({C,#}V)ʔ", "({C,#}V)ʔ"),
        ("{s,z}(ʔ)", "{s,sʔ,z,zʔ}"),
        ("a{i,j}(a)", "a{i,j,ia,ja}"),
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
        ("(V:[+long])θt", "{Vt:[+long],t:[+long]}", None),
        ("{s,z}(ʔ) {ʃ,ʒ}(ʔ) {ɬ,ɮ}(ʔ)", "s ʃ ɬ", "_#"),
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


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
@pytest.mark.parametrize(
    ("index", "section"),
    [
        ("Arapaho", "Proto-Arapaho-Atsina to Arapaho"),
        ("Gros Ventre", "Proto-Arapaho-Atsina to Gros Ventre"),
    ],
)
def test_v_long_n_apply_probe(tmp_path: Path, index: str, section: str):
    """Arapaho-V-longN / Gros-Ventre-V-longN: (V[-long])N → ∅ / _# on kaN, kN."""
    probe = tmp_path / "probe.wsca"
    probe.write_text("kaN\nkiN\nkN\n", encoding="utf-8")
    series = {
        "index": index,
        "section": section,
        "rules": [{"stages": ["(V[-long])N", "∅"], "env": "_#"}],
    }
    validate_asca(DiachronicSeries(series, "asca"), probe_words=probe)
