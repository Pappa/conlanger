"""Compile-time ASCA tone matrix attachment (ticket 62)."""

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.compile.asca.tone_matrices import normalize_asca_tone_matrices
from conlanger.tools.rules import DiachronicSeries
from conlanger.utils.file_io import feature_mappings_dict
from conlanger.utils.mappings import normalize_feature_matrices_in_field


@pytest.mark.parametrize(
    ("input", "expected"),
    [
        ("V[tone: 5]", "V:[tone: 5]"),
        ("V:[+long][tone: 51]", "V:[+long, tone: 51]"),
        ("V:[+long][tone: 21]", "V:[+long, tone: 21]"),
        ("a:[+long][tone: 35]", "a:[+long, tone: 35]"),
        ("V:[+stress][tone: 51]", "V:[+stress, tone: 51]"),
        ("V:[tone: 5]", "V:[tone: 5]"),
        ("{C,#}V:[+long][tone: 51]∅", "{C,#}V:[+long, tone: 51]∅"),
        ("V:[+stress]ː[tone: 51]", "V:[+stress]ː[tone: 51]"),
    ],
)
def test_normalize_asca_tone_matrices(input, expected):
    assert normalize_asca_tone_matrices(input) == expected


def test_length_then_tone_merge_for_index_length_mark():
    mapped = normalize_feature_matrices_in_field(
        "Vː[+falling tone]",
        feature_mappings_dict(),
    )
    assert mapped == "Vː[tone: 51]"


def test_compile_stress_length_tone_merges():
    assert (
        compile_asca_rule_fields("V:[+stress]ː[tone: 51]", "V", group_mappings={})
        == "V:[+stress, +long, tone: 51] > V"
    )


def test_cherokee_low_falling_tone_rule_validates():
    mappings = feature_mappings_dict()
    stage = normalize_feature_matrices_in_field(
        "Vː[+low falling tone]",
        mappings,
    )
    section = {
        "index": "37.1.1",
        "section": "Proto-Iroquoian to Cherokee",
        "rules": [{"stages": ["Vʔ", stage], "env": "_C"}],
    }
    validate_asca(DiachronicSeries(section, "asca", group_mappings={}))
