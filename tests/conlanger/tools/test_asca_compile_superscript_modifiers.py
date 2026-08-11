"""Tests for superscript segment modifier compile transforms (ticket 50)."""

import pytest

from conlanger.tools.asca_compile.superscript_modifiers import (
    normalize_asca_superscript_modifiers,
)
from conlanger.appliers.asca import validate_asca
from conlanger.tools.rules import (
    SoundChangeRuleSet,
    apply_asca_group_mappings_to_string,
    asca_group_mappings_dict,
)


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
    ],
)
def test_normalize_asca_superscript_modifiers(text, expected):
    mappings = asca_group_mappings_dict()
    transformed = normalize_asca_superscript_modifiers(text)
    assert apply_asca_group_mappings_to_string(transformed, mappings) == expected


def test_normalize_asca_superscript_modifiers_preserves_ticket_23_labial_regressions():
    mappings = asca_group_mappings_dict()
    text = "Kʷ > K / _V[+round]"
    expected = apply_asca_group_mappings_to_string(text, mappings)
    assert normalize_asca_superscript_modifiers(text) == text
    assert expected == (
        "C:[-front,+back,+hi,-lo,+round] > C:[-front,+back,+hi,-lo] / _V[+round]"
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
    assert normalize_asca_superscript_modifiers(text) == expected


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
def test_superscript_inventory_representatives_validate(inp, out, env):
    rule = {"stages": [inp, out]}
    if env:
        rule["env"] = env
    section = {"index": "1", "section": "superscript", "rules": [rule]}
    validate_asca(SoundChangeRuleSet(section, "asca"))


def test_superscript_s_aspirated_rule_compiles_via_pipeline():
    section = {
        "index": "1",
        "section": "superscript",
        "rules": [{"stages": ["Sʰ", "S"], "env": "#v_V"}],
    }
    ruleset = SoundChangeRuleSet(section, "asca")
    assert ruleset._parts[-1].value == "C:[+labial][+spread] > P / #v_V"
    validate_asca(ruleset)
