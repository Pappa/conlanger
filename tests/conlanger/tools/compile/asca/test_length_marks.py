"""Compile-time Index length mark → ASCA ``:[+long]`` (tickets 15, 25, 79)."""

import shutil
from pathlib import Path

import pytest

from conlanger.tools.compile.asca.length_marks import normalize_asca_length_marks
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.rules import DiachronicSeries


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("aː", "a:[+long]"),
        ("Vː", "V:[+long]"),
        ("tsː", "ts:[+long]"),
        ("VNC > VːC[+voiced]", "VNC > V:[+long]C[+voiced]"),
        ("tʷː", "tʷ:[+long]"),
        ("æː", "æ:[+long]"),
        ("{e,ɤ}ː", "{e,ɤ}:[+long]"),
        ("C_C{ː,C}V", "C_C{V:[+long],C}V"),
        ("s:[+long]ː", "s:[+long]"),
        ("0ː", "0:[+long]"),
        ("C=0 V0 > 0ː", "C=0 V0 > 0:[+long]"),
        ("V:[+stress]ː[tone: 51]", "V:[+stress, +long][tone: 51]"),
        ("V:[+stress]ː[-falling tone]", "V:[+stress, +long][-falling tone]"),
        (
            "S:[- voice]ː S:[+ voice]ː → hS S:[- voice]ː",
            "S:[- voice, +long] S:[+ voice, +long] → hS S:[- voice, +long]",
        ),
        ("Vː[tone: 51]", "V:[+long][tone: 51]"),
        ("%ː", "%:[+long]"),
        ("V:[+stress] > V:[+stress]ː", "V:[+stress] > V:[+stress, +long]"),
        ("P[- voice]ː", "P[- voice, +long]"),
        ("a", "a"),
        ("", ""),
    ],
)
def test_normalize_asca_length_marks(text, expected):
    assert normalize_asca_length_marks(text) == expected


def test_normalize_asca_length_marks_leaves_parenthesized_to_optional_length_pass():
    """Bare ``(ː)`` is expanded in ``optional_length`` before this pass runs."""
    from conlanger.tools.compile.asca.optional_length import (
        expand_optional_length_in_text,
    )

    assert normalize_asca_length_marks("V3(ː)ʔ") == "V3(ː)ʔ"
    assert expand_optional_length_in_text("V3(ː)ʔ") == "{V3ʔ,V3:[+long]ʔ}"
    assert normalize_asca_length_marks("1:[+stress] ː2") == "1:[+stress] ː2"
    assert (
        normalize_asca_length_marks(
            "{V:[+stress](C)(C)V:[+long],Vː:[+stress](C)(C)V:[+long]}"
        )
        == "{V:[+stress](C)(C)V:[+long],Vː:[+stress](C)(C)V:[+long]}"
    )


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_validate_asca_matrix_suffix_length_smoke():
    from conlanger.appliers.asca import validate_asca

    section = {
        "index": "37.1.2.6",
        "section": "Proto-Northern Iroquoian to Tuscarora",
        "rules": [
            {"stages": ["V:[+stress]ː", "V"], "env": "_C"},
            {"stages": ["P[- voice]ː", "P"], "env": "_#"},
        ],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


def test_compile_matrix_suffix_length_in_rule():
    assert (
        compile_asca_rule_fields("V:[+stress]ː[tone: 51]", "V")
        == "V:[+stress, +long, tone: 51] > V"
    )
