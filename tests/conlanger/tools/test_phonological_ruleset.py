import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from conlanger.tools.phonological_ruleset import PhonologicalRuleSet
from conlanger.tools.rules import (
    SoundChangeRuleSet,
    apply_asca_group_mappings_to_string,
    asca_group_mappings_dict,
)

_SAMPLE_MAPPINGS = {
    "R": "[+son,-syll]",
    "Z": "[+cont]",
    "E": "V:[+front]",
    "H": "[-place]",
    "S": "P",
    "U": "%",
}


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("VR", "V[+son,-syll]"),
        ("#_VR", "#_V[+son,-syll]"),
        ("{V,R}", "{V,[+son,-syll]}"),
        ("V_R", "V_[+son,-syll]"),
        ("{Z,C[-voice],r}", "{[+cont],C[-voice],r}"),
        ("#_V{Z,C[-voice],r}", "#_V{[+cont],C[-voice],r}"),
        ("VCH", "VC[-place]"),
        ("E_", "V:[+front]_"),
        ("{j,E}", "{j,V:[+front]}"),
        ("{R,h}", "{[+son,-syll],h}"),
        ("O_ in #U (not universal)", "O_ in #% (not universal)"),
        ("U[+long]", "%[+long]"),
        ("_V[+high +ATR]", "_V[+high +ATR]"),
        ("V[+high +ATR]", "V[+high +ATR]"),
        ("a", "a"),
        ("", ""),
    ],
)
def test_apply_asca_group_mappings_to_string(text, expected):
    assert apply_asca_group_mappings_to_string(text, _SAMPLE_MAPPINGS) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            "Kʷ > K",
            "C:[-front,+back,+hi,-lo,+round] > C:[-front,+back,+hi,-lo]",
        ),
        (
            "Kʷ > K / _V[+round]",
            "C:[-front,+back,+hi,-lo,+round] > C:[-front,+back,+hi,-lo] / _V[+round]",
        ),
        (
            "Kʷy > ɕ",
            "C:[-front,+back,+hi,-lo,+round]y > ɕ",
        ),
        (
            "i > ə / {P,K(ʷ),s}_",
            "i > ə / {C:[+labial],C:[-front,+back,+hi,-lo,+round],"
            "C:[-front,+back,+hi,-lo],s}_",
        ),
        (
            "Cʷ > C",
            "C:[+round] > C",
        ),
        (
            "Kr > k",
            "Kr > k",
        ),
        (
            "rK > k",
            "rK > k",
        ),
        (
            "Kw > k",
            "Kw > k",
        ),
    ],
)
def test_apply_asca_group_mappings_labialized_class_letters(text, expected):
    mappings = asca_group_mappings_dict()
    assert apply_asca_group_mappings_to_string(text, mappings) == expected


def test_sound_change_ruleset_applies_group_mappings_for_asca():
    section = {
        "index": "1.0",
        "section": "Test",
        "rules": [
            {
                "input": "f",
                "output": "p",
                "env": "#_V{Z,C[-voice],r}",
                "raw": "f → p / #_V{Z,C[-voice],r}",
                "source": "sample.html:1",
            }
        ],
    }
    rendered = str(
        SoundChangeRuleSet(section, "asca", group_mappings=_SAMPLE_MAPPINGS)
    )
    assert "[+cont]" in rendered
    assert "\tf > p / #_V{[+cont],C[-voice],r}" in rendered


def test_sound_change_ruleset_skips_group_mappings_for_brassica():
    section = {
        "index": "1.0",
        "section": "Test",
        "rules": [{"input": "S", "output": "P", "env": "{V,R}_V"}],
    }
    rendered = str(
        SoundChangeRuleSet(section, "brassica", group_mappings=_SAMPLE_MAPPINGS)
    )
    assert rendered.endswith("S / P / {V,R}_V")


def test_phonological_ruleset_does_not_mutate_corpus_rules():
    section = {
        "index": "1.0",
        "section": "Test",
        "rules": [
            {
                "input": "f",
                "output": "p",
                "env": "#_V{Z,C[-voice],r}",
                "raw": "f → p / #_V{Z,C[-voice],r}",
                "source": "sample.html:1",
            }
        ],
    }
    prs = PhonologicalRuleSet(section)
    assert prs.section["rules"][0]["env"] == "#_V{Z,C[-voice],r}"
    rendered = str(prs.to_sound_change_ruleset(group_mappings=_SAMPLE_MAPPINGS))
    assert "[+cont]" in rendered


def test_asca_group_mappings_dict_loads_package_csv():
    mappings = asca_group_mappings_dict()
    assert mappings["R"] == "[+son,-syll]"
    assert mappings["Z"] == "[+cont]"


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_phonological_ruleset_validates_labialized_class_letter_fixtures():
    section = {
        "index": "17.10",
        "section": "PIE labiovelars",
        "rules": [
            {
                "input": "Kʷ",
                "output": "K",
                "env": "",
                "raw": "Kʷ → K",
                "source": "index_diachronica.html:334",
            },
            {
                "input": "i",
                "output": "ə",
                "env": "{P,K(ʷ),s}_",
                "raw": "i → ə / {P,K(ʷ),s}_",
                "source": "index_diachronica.html:7340",
            },
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    from conlanger.tools.asca_validator import validate_asca

    validate_asca(PhonologicalRuleSet(section).to_sound_change_ruleset(), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_phonological_ruleset_validates_known_unknown_grouping_fixtures():
    section = {
        "index": "6.2.2.1.2",
        "section": "Proto-Boreafrasian to Egypto-Berber",
        "rules": [
            {
                "input": "f",
                "output": "p",
                "env": "#_V{Z,C[-voice],r}",
                "raw": "f → p / #_V{Z,C[-voice],r}",
                "source": "index_diachronica_original.html:1261",
            },
            {
                "input": "ʕ",
                "output": "i",
                "env": "#_VR",
                "raw": "ʕ → i / #_VR",
                "source": "index_diachronica_original.html:1274",
            },
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    from conlanger.tools.asca_validator import validate_asca

    validate_asca(PhonologicalRuleSet(section).to_sound_change_ruleset(), probe_words=probe)


@patch("conlanger.tools.corpus_inventory.validate_asca", return_value=True)
def test_corpus_inventory_uses_phonological_ruleset(_mock_validate):
    from conlanger.tools.corpus_inventory import validate_corpus_rule

    section = {"index": "1.0", "section": "Test Section"}
    rule = {
        "input": "f",
        "output": "p",
        "env": "#_V{Z,C[-voice],r}",
        "raw": "f → p / #_V{Z,C[-voice],r}",
        "source": "sample.html:1",
    }
    validate_corpus_rule(section, rule, 0, probe_words=Path("/probe.wsca"))
    passed_rule = _mock_validate.call_args[0][0]
    rendered = str(passed_rule)
    assert "[+cont]" in rendered
    assert "Z" not in rendered.split("\t")[1]
