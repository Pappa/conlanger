"""Tests for Index dot-affricate / cluster notation compile transforms (ticket 118)."""

import shutil
from pathlib import Path

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.dot_affricate import normalize_dot_affricate_notation
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.rules import DiachronicSeries


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # Indo-Iranian affricates
        ("t.ʃ", "tʃ"),
        ("d.ʒʱ", "dʒʱ"),
        ("t.s", "ts"),
        ("t.ʂ", "tʂ"),
        ("t.ɕ", "tɕ"),
        ("t.C", "tC"),
        ("ttʃ ddʒʱ > t.ʃ d.ʒʱ", "ttʃ ddʒʱ > tʃ dʒʱ"),
        ("t.ʂ t.ɕ > kʂ cʰ:[+long]", "tʂ tɕ > kʂ cʰ:[+long]"),
        (
            "s:[+long] ʂ:[+long] ɕ:[+long] > t.s t.ʂ t.C",
            "s:[+long] ʂ:[+long] ɕ:[+long] > ts tʂ tC",
        ),
        # Tibeto-Burman cluster notation
        ("p.", "p"),
        ("tr.", "tr"),
        ("ç.w", "çw"),
        ("s.d", "sd"),
        ("m.p", "mp"),
        ("n.br", "nbr"),
        ("p.j", "pj"),
        ("ç.k", "çk"),
        ("k.r", "kr"),
        ("e.i", "ei"),
        ("ɡ.", "ɡ"),
        ("n.pj.", "npj"),
        ("m.t.", "mt"),
        ("(ç.)tr", "(ç)tr"),
        ("s.{ts,pj}", "s{ts,pj}"),
        ("{s.ts,br}", "{sts,br}"),
        (
            "p çp b > p. ç.w p rp. kj m.p n.br p.j",
            "p çp b > p çw p rp kj mp nbr pj",
        ),
        (
            "t st tr d > t. s.d tr. t s.t (ç.)tr m.t. n.dr ɡ.t",
            "t st tr d > t sd tr t st (ç)tr mt ndr ɡt",
        ),
        # Stress + segment (Spanish)
        (
            "je:[+stress].o je:[+stress].a > {i:[+stress].o,j:[+stress]o} i:[+stress].a",
            "je:[+stress]o je:[+stress]a > {i:[+stress]o,j:[+stress]o} i:[+stress]a",
        ),
        # dot_inside_set with subscript digits
        ("{i3,e3} > {i3.ə3}", "{i3,e3} > {i3ə3}"),
        # dot_inside_set env
        ("N > m / _{ŋ.nj}", "N > m / _{ŋnj}"),
        # preserve range dots
        ("a..o", "a..o"),
        ("V..V", "V..V"),
        # bracket-safe: feature matrices untouched
        ("[+long]", "[+long]"),
        ("", ""),
        ("no dots", "no dots"),
    ],
)
def test_normalize_dot_affricate_notation(text, expected):
    assert normalize_dot_affricate_notation(text) == expected


@pytest.mark.parametrize(
    ("inp", "out", "env", "expected_compiled"),
    [
        ("ttʃ ddʒʱ", "t.ʃ d.ʒʱ", None, "ttʃ ddʒʱ > tʃ dʒʱ"),
        ("t.ʂ t.ɕ", "kʂ cʰ:[+long]", None, "tʂ tɕ > kʂ cʰ:[+long]"),
        (
            "s:[+long] ʂ:[+long] ɕ:[+long]",
            "t.s t.ʂ t.C",
            None,
            "s:[+long] ʂ:[+long] ɕ:[+long] > ts tʂ tC",
        ),
        (
            "p çp b rC:[+labial] Np Nb pr {br,pj}",
            "p. ç.w p rp. kj m.p n.br p.j",
            None,
            "p çp b rC:[+labial] Np Nb pr {br,pj} > p çw p rp kj mp nbr pj",
        ),
        ("Nç", "n.pj.", None, "Nç > npj"),
        ("C:[+labial]ç", "b.ç", None, "C:[+labial]ç > bç"),
    ],
)
def test_compile_asca_rule_fields_dot_affricate(inp, out, env, expected_compiled):
    assert compile_asca_rule_fields(inp, out, env) == expected_compiled


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
@pytest.mark.parametrize(
    ("inp", "out", "env"),
    [
        ("ttʃ ddʒʱ", "t.ʃ d.ʒʱ", None),
        ("t.ʂ t.ɕ", "kʂ cʰ:[+long]", None),
        ("s:[+long] ʂ:[+long] ɕ:[+long]", "t.s t.ʂ t.C", None),
        (
            "p çp b rC:[+labial] Np Nb pr {br,pj}",
            "p. ç.w p rp. kj m.p n.br p.j",
            None,
        ),
        ("Nç", "n.pj.", None),
        ("C:[+labial]ç", "b.ç", None),
        ("N", "m", "_{ŋ.nj}"),
        ("ts dʒ NP:[-voice]P", "{s,tʃ.} tʃ. m", None),
    ],
)
def test_dot_affricate_inventory_rules_validate(inp, out, env):
    rule: dict[str, object] = {"stages": [inp, out]}
    if env is not None:
        rule["env"] = env
    section = {
        "index": "17.10",
        "section": "dot affricate smoke",
        "rules": [rule],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)
