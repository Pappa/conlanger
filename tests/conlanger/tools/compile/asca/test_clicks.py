"""Tests for Index Khoisan click compile transforms (ticket 136)."""

import shutil
from pathlib import Path

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.clicks import normalize_asca_index_click_segments
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.rules import DiachronicSeries


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("!", "k!"),
        ("!!", "k! k!"),
        ("! !ˀ !̬ !̃", "k! k!:[+cg] k!̬ k!̃"),
        ("{ǀ̃,ǀ̃n}", "{kǀ̃,kǀ̃n}"),
        ("{ǀ̃,ǀ̃n} > ǂ̃n", "{kǀ̃,kǀ̃n} > kǂ̃n"),
        ("!! > ǁ", "k! k! > kǁ"),
        (
            "ǂ {ǂ̃n,ǂˀ,ǂx:[+cg]} > ǂɡ ǂ",
            "kǂ {kǂ̃n,kǂ:[+cg],kǂx:[+cg]} > ɡǂ kǂ",
        ),
        ("{ǀˀ,ǀx:[+cg]}", "{kǀ:[+cg],kǀx:[+cg]}"),
        ("!! ʘ > ǁ ǀ", "k! k! kʘ > kǁ kǀ"),
        ("ǂ > !!", "kǂ > k! k!"),
        ("", ""),
        ("no clicks", "no clicks"),
    ],
)
def test_normalize_asca_index_click_segments(text, expected):
    assert normalize_asca_index_click_segments(text) == expected


@pytest.mark.parametrize(
    ("inp", "out", "env", "expected_compiled"),
    [
        ("!", "k", None, "k! > k"),
        (
            "! !ˀ !̬ !̃",
            "k ɡ ŋɡ",
            None,
            "k! k!:[+cg] k!̬ k!̃ > k ɡ ŋɡ",
        ),
        ("!!", "ǁ", None, "k! k! > kǁ"),
        (
            "tj sj dj zj",
            "tʃ ʃ dʒ ʒ",
            "! _uː",
            "tj sj dj zj > tʃ ʃ dʒ ʒ / ! _u:[+long]",
        ),
    ],
)
def test_compile_asca_rule_fields_index_clicks(inp, out, env, expected_compiled):
    assert compile_asca_rule_fields(inp, out, env) == expected_compiled


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
@pytest.mark.parametrize(
    ("inp", "out", "env"),
    [
        ("! !ˀ !̬ !̃", "k ɡ ŋɡ", None),
        ("{ǀ̃,ǀ̃n}", "ǂ̃n", None),
        ("!! ʘ", "ǁ ǀ", None),
        ("ǂ", "!!", None),
    ],
)
def test_index_click_rules_validate(inp, out, env):
    rule: dict[str, object] = {"stages": [inp, out]}
    if env is not None:
        rule["env"] = env
    section = {
        "index": "20.1.3",
        "section": "Khoisan click smoke",
        "rules": [rule],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)
