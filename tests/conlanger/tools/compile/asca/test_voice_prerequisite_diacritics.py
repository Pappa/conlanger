"""Tests for voice-prerequisite aspiration compile transforms (ticket 110)."""

import shutil
from pathlib import Path

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.compile.asca.voice_prerequisite_diacritics import (
    normalize_asca_voice_prerequisite_diacritics,
)
from conlanger.tools.rules import DiachronicSeries


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("jʰ", "j:[+spread,+voice]"),
        ("bʰ dʰ gʰ", "b:[+spread,+voice] d:[+spread,+voice] g:[+spread,+voice]"),
        ("ɡʲʰ gʷʰ", "ɡʲ:[+spread,+voice] gʷ:[+spread,+voice]"),
        ("ɢʷʰ", "ɢʷ:[+spread,+voice]"),
        ("pwʰ", "pʷʰ"),
        ("bwʰ", "bw:[+spread,+voice]"),
        ("twʰ", "tʷʰ"),
        ("lʰ rʰ", "l:[+spread,+voice] r:[+spread,+voice]"),
        ("tʰ pʰ cʰ", "tʰ pʰ cʰ"),
        ("C[-voice]ʰ", "C[-voice]ʰ"),
        ("z > jʰ", "z > j:[+spread,+voice]"),
        ("jʰ > h / _i", "j:[+spread,+voice] > h / _i"),
        (
            "p:[+long] pw:[+long] > pʰ pwʰ jʰ",
            "p:[+long] pw:[+long] > pʰ pʷʰ j:[+spread,+voice]",
        ),
        ("b:[+spread,+voice][+long]", "b:[+spread,+voice][+long]"),
        ("", ""),
    ],
)
def test_normalize_asca_voice_prerequisite_diacritics(text, expected):
    assert normalize_asca_voice_prerequisite_diacritics(text) == expected


@pytest.mark.parametrize(
    ("inp", "out", "env", "expected_compiled"),
    [
        (
            "z",
            "jʰ",
            None,
            "z > j:[+spread,+voice]",
        ),
        (
            "jʰ",
            "h",
            "_i",
            "j:[+spread,+voice] > h / _i",
        ),
        (
            "pː pwː tː ʈː qː kː",
            "pʰ pwʰ cʰ tʰ h jʰ",
            None,
            (
                "p:[+long] pw:[+long] t:[+long] ʈ:[+long] q:[+long] k:[+long] > "
                "pʰ pʷʰ cʰ tʰ h j:[+spread,+voice]"
            ),
        ),
        (
            "bʰ dʰ gʰ",
            "pʰ tʰ dʰ",
            None,
            (
                "b:[+spread,+voice] d:[+spread,+voice] g:[+spread,+voice] > "
                "pʰ tʰ d:[+spread,+voice]"
            ),
        ),
        (
            "ɡʲʰ gʷʰ",
            "ɡʰ xʷ",
            None,
            "ɡʲ:[+spread,+voice] gʷ:[+spread,+voice] > ɡ:[+spread,+voice] xʷ",
        ),
        (
            "pː pwː tː ʈ kː cː",
            "f hʷ tʰ lʰ h s",
            None,
            (
                "p:[+long] pw:[+long] t:[+long] ʈ k:[+long] c:[+long] > "
                "f hʷ tʰ l:[+spread,+voice] h s"
            ),
        ),
    ],
)
def test_compile_asca_rule_fields_voice_prerequisite_diacritics(
    inp, out, env, expected_compiled
):
    assert compile_asca_rule_fields(inp, out, env) == expected_compiled


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
@pytest.mark.parametrize(
    ("inp", "out", "env"),
    [
        ("z", "jʰ", None),
        ("jʰ", "h", "_i"),
        (
            "pː pwː tː ʈː qː kː",
            "pʰ pwʰ cʰ tʰ h jʰ",
            None,
        ),
        ("bʰ dʰ gʰ", "pʰ tʰ dʰ", None),
        ("ɡʲʰ gʷʰ", "ɡʰ xʷ", None),
        ("jʰ", "θ", None),
        ("jʰ j", "s z", None),
    ],
)
def test_voice_prerequisite_inventory_rules_validate(inp, out, env):
    rule: dict[str, object] = {"stages": [inp, out]}
    if env is not None:
        rule["env"] = env
    section = {
        "index": "10.3.5.1",
        "section": "voice prerequisite smoke",
        "rules": [rule],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)
