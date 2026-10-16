"""Tests for prenasal ⁿ prefix compile transforms (ticket 117)."""

import pytest

from conlanger.compile.tools.asca.pipeline import compile_asca_rule_fields
from conlanger.compile.tools.asca.prenasal_prefix import normalize_prenasal_prefix


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("ⁿP", "N P"),
        ("P > ⁿP", "P > N P"),
        ("ⁿP > N", "N P > N"),
        ("NP > ⁿP", "NP > N P"),
        ("NVP > VⁿP", "NVP > V N P"),
        ("s ʃ > ⁿs ⁿʃ", "s ʃ > N s N ʃ"),
        ("N[-tense] N[+tense] > N[+tense] ⁿP", "N[-tense] N[+tense] > N[+tense] N P"),
        ("ⁿd", "ⁿd"),
        ("ⁿt", "ⁿt"),
        ("k ⁿd ŋ", "k ⁿd ŋ"),
        ("N[+nasal] ⁿP", "N[+nasal] N P"),
        ("(ⁿ)d", "(ⁿ)d"),
        ("", ""),
        ("no prenasal", "no prenasal"),
    ],
)
def test_normalize_prenasal_prefix(text, expected):
    assert normalize_prenasal_prefix(text) == expected


@pytest.mark.parametrize(
    ("inp", "out", "env", "expected_compiled"),
    [
        ("P", "ⁿP", "#NV_", "P > N P / #NV_"),
        ("s ʃ", "ⁿs ⁿʃ", "_ %[-nas]", "s ʃ > N s N ʃ / _ %[-nas]"),
        ("NP", "ⁿP", None, "NP > N P"),
        ("ⁿP", "N", "_#", "N P > N / _#"),
        ("NVP", "VⁿP", "#_", "NVP > V N P / #_"),
        (
            "N[-tense] N[+tense]",
            "N[+tense] ⁿP",
            "_ C=2 position",
            "N:[-tense] N:[+tense] > N:[+tense] N P / _ C=2 position",
        ),
    ],
)
def test_compile_asca_rule_fields_prenasal_prefix(inp, out, env, expected_compiled):
    assert compile_asca_rule_fields(inp, out, env) == expected_compiled
