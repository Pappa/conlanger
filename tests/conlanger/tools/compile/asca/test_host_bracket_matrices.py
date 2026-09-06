"""Compile-time host+bracket matrix → colon form (ticket 121)."""

import shutil
from pathlib import Path

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.host_bracket_matrices import (
    host_bracket_matrix_to_colon,
    normalize_asca_host_bracket_matrices,
)
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.compile.compile_fields import RuleInput, RuleOutput
from conlanger.tools.rules import DiachronicSeries, SoundChangeRule


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


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_v_long_to_v_short_output_substitution_apply_probe(tmp_path: Path):
    """V:[+long] > V:[-long] substitutes long vowels to short."""
    probe = tmp_path / "probe.wsca"
    probe.write_text("a:.i:\n", encoding="utf-8")
    section = {
        "index": "121",
        "section": "host-bracket-matrices",
        "rules": [{"stages": ["Vː", "V[-long]"]}],
    }
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_lemerig_acv_template_apply_probe():
    """Oceanic CV templates keep bracket form; colon rewrite panics at apply."""
    section = {
        "index": "10.3.3",
        "section": "Proto-Oceanic to Lemerig",
        "rules": [{"stages": ["aCV[+ high]", "{ɛ,œ}C"]}],
    }
    validate_asca(DiachronicSeries(section, "asca"))


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_v_short_input_matching_apply_probe(tmp_path: Path):
    """Input V:[-long] matches short vowels only."""
    probe = tmp_path / "probe.wsca"
    probe.write_text("a.\ni:\n", encoding="utf-8")
    section = {
        "index": "121",
        "section": "host-bracket-matrices-input",
        "rules": [{"stages": ["V[-long]", "x"]}],
    }
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)
