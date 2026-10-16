"""Tests for Index segment diacritic compile transforms (ticket 135)."""

import pytest

from conlanger.compile.tools.asca.pipeline import compile_asca_rule_fields
from conlanger.compile.tools.asca.segment_diacritics import (
    normalize_index_segment_diacritics,
)
from conlanger.scripts.config_loaders import load_compiler_config


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("r̝̊ r̝", "ʂ ʐ"),
        ("s̺", "s:[+dist,+cor,+ant]"),
        ("_{s̺,s̻}", "_{s:[+dist,+cor,+ant],s:[+dist,+cor]}"),
        ("_V̂", "_V:[+long]"),
        ("b̚ ɡ̚", "b:[-cont] ɡ:[-cont]"),
        ("C > ∅ / C=1 _C=2 // C₂ = {r,l}", "C > ∅ / C=1 _C=2 // C=2 = {r,l}"),
        ("plain", "plain"),
    ],
)
def test_normalize_index_segment_diacritics(text, expected):
    assert normalize_index_segment_diacritics(text) == expected


def test_compile_uto_aztecan_vowel_series_env():
    cfg = load_compiler_config()
    compiled = compile_asca_rule_fields(
        "s", "∅", "Vₙ_", section_index="43.1", compiler_config=cfg
    )
    assert compiled == "s > ∅ / V:[+nas]_"
