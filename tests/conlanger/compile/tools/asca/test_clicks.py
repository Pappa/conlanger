"""Tests for Index Khoisan click compile transforms (ticket 136)."""

import pytest

from conlanger.compile.tools.asca.clicks import normalize_asca_index_click_segments
from conlanger.compile.tools.asca.pipeline import compile_asca_rule_fields


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
