"""Tests for superscript segment modifier compile transforms (ticket 50)."""

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.group_mappings import (
    apply_asca_group_mappings_to_string,
)
from conlanger.tools.compile.asca.superscript_modifiers import (
    normalize_asca_superscript_modifiers,
)
from conlanger.tools.rules import DiachronicSeries


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("C:[+long] > Cʰ", "C:[+long] > C:[+spread]"),
        ("C > Cʲ / _V", "C > C:[+cor,+dist] / _V"),
        ("Cʱ > C", "C:[+spread,+voice] > C"),
        ("Sʰ > S / #v_V", "C:[+labial][+spread] > P / #v_V"),
        ("Ci > Cʲə", "Ci > C:[+cor,+dist]ə"),
        ("Ce Ce:[+long] > Cʲə Cʲɛ", "Ce Ce:[+long] > C:[+cor,+dist]ə C:[+cor,+dist]ɛ"),
        ("mV[-long] > ∅ / #_{ʰC,s,ʃ}", "mV[-long] > ∅ / #_{C:[+spread],s,ʃ}"),
        ("{d,n}ʲ > j / #_", "{d,dʲ,n,nʲ} > j / #_"),
        ("e:[+long] > ia / _{#,Cʲ}", "e:[+long] > ia / _{#,C:[+cor,+dist]}"),
        ("{L,Lʲ} > r", "{L,L:[+cor,+dist]} > r"),
        (
            "Pʲ > C:[+labial] / _C",
            "C:[+labial,+cor,+dist] > C:[+labial] / _C",
        ),
        (
            "Kʷ > K / _V[+round]",
            "C:[-front,+back,+hi,-lo,+round] > C:[-front,+back,+hi,-lo] / _V[+round]",
        ),
    ],
)
def test_normalize_asca_superscript_modifiers(text, expected, fx_sample_group_mappings):
    transformed = normalize_asca_superscript_modifiers(text, fx_sample_group_mappings)
    assert (
        apply_asca_group_mappings_to_string(transformed, fx_sample_group_mappings)
        == expected
    )


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Kr > k", "Kr > k"),
        ("rK > k", "rK > k"),
        ("Kw > k", "Kw > k"),
        ("tʰ > d", "tʰ > d"),
        ("kʷ > w", "kʷ > w"),
        ("lʲ > r", "lʲ > r"),
    ],
)
def test_normalize_asca_superscript_modifiers_leaves_boundaries_and_ipa_literals(
    text, expected
):
    assert normalize_asca_superscript_modifiers(text, {}) == expected


@pytest.mark.parametrize(
    ("inp", "out", "env"),
    [
        ("C:[+long]", "C:[+spread]", ""),
        ("C", "C:[+cor,+dist]", "_V"),
        ("mV[-long]", "∅", "#_{C:[+spread],s,ʃ}"),
        ("{L,L:[+cor,+dist]}", "r", ""),
        ("C:[+labial][+spread]", "P", "#v_V"),
        ("Sʰ", "S", "#v_V"),
        ("e:[+long]", "ia", "_{#,C:[+cor,+dist]}"),
    ],
)
def test_superscript_inventory_representatives_validate(
    inp, out, env, fx_sample_group_mappings
):
    rule = {"stages": [inp, out]}
    if env:
        rule["env"] = env
    section = {"index": "1", "section": "superscript", "rules": [rule]}
    validate_asca(
        DiachronicSeries(section, "asca", group_mappings=fx_sample_group_mappings)
    )


def test_superscript_s_aspirated_rule_compiles_via_pipeline(fx_sample_group_mappings):
    section = {
        "index": "1",
        "section": "superscript",
        "rules": [{"stages": ["Sʰ", "S"], "env": "#v_V"}],
    }
    ruleset = DiachronicSeries(section, "asca", group_mappings=fx_sample_group_mappings)
    assert ruleset._parts[-1].value == "C:[+labial][+spread] > P / #v_V"
    validate_asca(ruleset)
