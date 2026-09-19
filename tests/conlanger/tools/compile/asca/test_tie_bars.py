"""Tests for Index affricate tie bar → ASCA tie (ticket 135)."""

import shutil
from pathlib import Path

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.compile.asca.tie_bars import normalize_index_affricate_tie_bars
from conlanger.tools.rules import DiachronicSeries

_INDEX_TIE = "\u035c"
_ASCA_TIE = "\u0361"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("t͜s", f"t{_ASCA_TIE}s"),
        ("d͜z t͜s", f"d{_ASCA_TIE}z t{_ASCA_TIE}s"),
        ("_{t͜s,s}", f"_{{t{_ASCA_TIE}s,s}}"),
        ("k͜p", f"k{_ASCA_TIE}p"),
        ("ǀʰ͜q", f"ǀʰ{_ASCA_TIE}q"),
        ("no tie", "no tie"),
        ("", ""),
    ],
)
def test_normalize_index_affricate_tie_bars(text, expected):
    assert normalize_index_affricate_tie_bars(text) == expected


def test_compile_asca_rule_fields_tie_bars_moroccan():
    compiled = compile_asca_rule_fields(
        "t", f"t{_INDEX_TIE}s", None, section_index="6.2.2.1.14"
    )
    assert compiled == f"t > t{_ASCA_TIE}s"


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_validate_asca_tie_bar_inventory_smoke():
    section = {
        "index": "6.2.2.1.14",
        "section": "Moroccan Arabic",
        "rules": [{"stages": ["t", f"t{_INDEX_TIE}s"]}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)
