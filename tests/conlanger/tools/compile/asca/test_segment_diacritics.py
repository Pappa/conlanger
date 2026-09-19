"""Tests for Index segment diacritic compile transforms (ticket 135)."""

import shutil
from pathlib import Path

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.scripts.config_loaders import load_compiler_config
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.compile.asca.segment_diacritics import (
    normalize_index_segment_diacritics,
)
from conlanger.tools.rules import DiachronicSeries


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


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
@pytest.mark.parametrize(
    ("index", "stages", "env"),
    [
        ("43.1", ["s", "∅"], "Vₙ_"),
        ("44.2", ["s̺", "tʃ"], "#_"),
        ("17.11.1", ["r̝̊ r̝", "ʂ ʐ"], None),
    ],
)
def test_validate_asca_segment_diacritic_smoke(index, stages, env):
    rule: dict[str, object] = {"stages": stages}
    if env is not None:
        rule["env"] = env
    section = {"index": index, "section": "smoke", "rules": [rule]}
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(
        DiachronicSeries(
            section,
            "asca",
            compiler_config=load_compiler_config(),
        ),
        probe_words=probe,
    )
