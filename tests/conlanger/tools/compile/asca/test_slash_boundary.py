"""Tests for residual output/env slash-boundary compile transforms (ticket 82)."""

import shutil
from pathlib import Path

import pytest

from conlanger.tools.compile.asca.slash_boundary import (
    drop_concatenated_deletion_column,
)
from conlanger.tools.rules import DiachronicSeries


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("{C,#,V:[+long]}∅ / _C", "{C,#,V:[+long]} / _C"),
        (
            "({C,#}Vː[+falling tone])∅ / _C",
            "({C,#}Vː[+falling tone]) / _C",
        ),
        (
            "{C,#,V:[+long, tone: 51]}∅ / _C",
            "{C,#,V:[+long, tone: 51]} / _C",
        ),
        ("{∅,h}", "{∅,h}"),
        ("χ > h / #_", "χ > h / #_"),
        ("", ""),
    ],
)
def test_drop_concatenated_deletion_column(text, expected):
    assert drop_concatenated_deletion_column(text) == expected


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_validate_asca_slash_boundary_representatives():
    from conlanger.appliers.asca import validate_asca

    probe = Path("tests/fixtures/asca_probe_words.wsca")
    section = {
        "index": "82",
        "section": "slash-boundary",
        "rules": [
            {"stages": ["χ", "h"], "env": "#_"},
            {"stages": ["d ɡ", "t k"]},
            {"stages": ["Cʔ", "{C}∅"], "env": "_C"},
            {"stages": ["eː ow", "ej (əw)"]},
        ],
    }
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)
