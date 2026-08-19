"""Tests for Index breve vowel notation → ASCA compile transform (ticket 84)."""

import shutil
from pathlib import Path

import pytest

from conlanger.tools.compile.asca.breve_marks import normalize_asca_breve_marks
from conlanger.tools.rules import DiachronicSeries


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("iə > j̆ / _C%", "iə > j / _C%"),
        ("ɨə > ɨ̆ / _C%", "ɨə > ɨ / _C%"),
        ("ɨ̆ i̯o > u ə", "ɨ i̯o > u ə"),
        ("ɨ̆ > a / _K", "ɨ > a / _K"),
        ("ɨ̆ə > ɨ̆ / _C%", "ɨə > ɨ / _C%"),
        ("ɛ iɛ > e:[+long] j̆", "ɛ iɛ > e:[+long] j"),
        ("∅ > ə̆ / _{n,r}", "∅ > ə:[-long] / _{n,r}"),
        (
            "ɑ ə ʊ > {æ̆,ă} æ̆ ŏ",
            "ɑ ə ʊ > {æ:[-long],a:[-long]} æ:[-long] o:[-long]",
        ),
        ("a", "a"),
        ("", ""),
    ],
)
def test_normalize_asca_breve_marks(text, expected):
    assert normalize_asca_breve_marks(text) == expected


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_validate_asca_breve_marks_tai_scots_smoke():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "38.1.1.3",
        "section": "Proto-Tai to Central Tai",
        "rules": [
            {"stages": ["iə", "j̆"], "env": "_C%"},
            {"stages": ["ɨə", "ɨ̆"], "env": "_C%"},
            {"stages": ["ɨ̆ i̯o", "u ə"]},
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_validate_asca_breve_marks_scots_smoke():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "17.7.2.1.10",
        "section": "Old English to Scots",
        "rules": [{"stages": ["∅", "ə̆"], "env": "_{n,r}"}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_validate_asca_breve_marks_tanacross_smoke():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "29.1.1.1.37",
        "section": "Proto-Athabaskan to Tanacross",
        "rules": [{"stages": ["ɑ ə ʊ", "{æ̆,ă} æ̆ ŏ"]}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)
