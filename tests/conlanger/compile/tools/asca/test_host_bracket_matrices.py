"""Compile-time host+bracket matrix → colon form (ticket 121)."""

import pytest

from conlanger.compile.models.compile_fields import RuleInput, RuleOutput
from conlanger.compile.models.rules import SoundChangeRule
from conlanger.compile.tools.asca.host_bracket_matrices import (
    host_bracket_matrix_to_colon,
    normalize_asca_host_bracket_matrices,
)
from conlanger.compile.tools.asca.pipeline import compile_asca_rule_fields


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        ("V[-long]", "V:[-long]"),
        ("C[+voice]", "C:[+voice]"),
        ("V:[-long]", "V:[-long]"),
        ("[-long]", "[-long]"),
        ("plain", "plain"),
    ],
)
def test_host_bracket_matrix_to_colon(token, expected):
    assert host_bracket_matrix_to_colon(token) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("V[-long]", "V:[-long]"),
        ("C[+voice]", "C:[+voice]"),
        ("V:[+long] > V[-long]", "V:[+long] > V:[-long]"),
        ("{C[+voice],C[-voice]}", "{C:[+voice],C:[-voice]}"),
        ("[-long]", "[-long]"),
        ("[+] > [+voice]", "[+] > [+voice]"),
        ("a[+nas]", "a:[+nas]"),
        ("aCV[+ high]", "aCV[+ high]"),
        ("mV[-long]", "mV:[-long]"),
        ("V:[+long]", "V:[+long]"),
        ("", ""),
    ],
)
def test_normalize_asca_host_bracket_matrices(text, expected):
    assert normalize_asca_host_bracket_matrices(text) == expected


def test_compile_asca_rule_fields_rewrites_io_host_bracket_matrices():
    assert compile_asca_rule_fields("Vː", "V[-long]") == "V:[+long] > V:[-long]"


def test_sound_change_rule_preserves_raw_io_tokens():
    rule = SoundChangeRule(
        input=RuleInput.from_raw("Vː"),
        output=RuleOutput.from_raw("V[-long]"),
        raw="Vː → V[-long]",
        detect_alternatives=False,
    )
    assert rule.input.raw == "Vː"
    assert rule.output.raw == "V[-long]"
    assert rule.raw == "Vː → V[-long]"
    assert rule.value == "V:[+long] > V:[-long]"
