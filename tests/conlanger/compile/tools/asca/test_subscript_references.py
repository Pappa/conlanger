"""Tests for compile-time positional/identity subscript expansion (ticket 40)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.compile.models.rules import DiachronicSeries
from conlanger.compile.tools.asca.pipeline import compile_asca_rule_fields
from conlanger.compile.tools.asca.subscript_references import (
    expand_subscript_references_across_fields,
)

_FieldQuad = tuple[str, str, str | None, str | None]


@pytest.mark.parametrize(
    ("inp", "output", "env", "exception", "expected"),
    [
        ("C₁C₂", "C₂", None, None, ("C=1 C=2", "2", None, None)),
        ("V₀V₀", "V₀", None, None, ("V=0 0", "0", None, None)),
        ("h", "ʔ", "V₀V₀", None, ("h", "ʔ", "_ V=0 0", None)),
        ("C", "V", "[+high]", None, ("C", "V", "[+high]", None)),
        (
            "V₀[+nas]V₀[-nas]",
            "V₀[+nas]",
            None,
            None,
            ("V:[+nas]=0 V:[-nas]=0", "0:[+nas]", None, None),
        ),
        ("C₁[+high]", "C₂", None, None, ("C:[+high]=1", "C=2", None, None)),
        (
            "CV₁CV:[+stress]₂",
            "CV₂CV:[+stress]₂",
            None,
            None,
            ("CV=1 CV:[+stress]=2", "2 2:[+stress]", None, None),
        ),
        ("h", "ʔ", "V₀", None, ("h", "ʔ", "_ V=0", None)),
        ("C₁", "C₂", None, "except _#", ("C=1", "C=2", None, "except _#")),
        ("C₁C₁", "C₁", None, None, ("C=1 1", "1", None, None)),
        ("C₁C₂", "", None, None, ("C=1 C=2", "", None, None)),
        (
            "C₁ˤC₂",
            "C₁C₂ˤ",
            None,
            None,
            ("C:[+pharyn]=1 C=2", "1 2:[+pharyn]", None, None),
        ),
        ("mn", "mV₀nV₀", "#_", None, ("mn", "mV=0 n0", "#_", None)),
        ("CʔV₀", "CV₀ʔV₀", None, None, ("CʔV=0", "C0 ʔ0", None, None)),
        ("C₀VC₀", "C₀ː", None, None, ("C=0 V0", "0ː", None, None)),
        (
            "C₁C₂C₃C₄",
            "(C₃)C₄",
            None,
            None,
            ("C=1 C=2 C=3 C=4", "{3}4", None, None),
        ),
        (
            "C₁C₂",
            "xC₂",
            "if C₂ was a plosive or s",
            None,
            ("C=1 C=2", "x2", "if C₂ was a plosive or s", None),
        ),
        (
            "ɣ",
            "ʔ",
            "VV₀_V₀",
            "V₀ = U",
            ("ɣ", "ʔ", "VV=0 _0", "V₀ = U"),
        ),
    ],
)
def test_expand_subscript_references_across_fields(
    inp: str,
    output: str,
    env: str | None,
    exception: str | None,
    expected: _FieldQuad,
) -> None:
    assert (
        expand_subscript_references_across_fields(inp, output, env, exception)
        == expected
    )


def test_compile_pipeline_applies_subscript_expansion_before_group_mappings():
    inp, output = "C₁C₂", "C₂"
    assert compile_asca_rule_fields(inp, output) == "C=1 C=2 > 2"


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_rule_change_validates_positional_slot_fixture():
    section = {
        "index": "10.2.1",
        "section": "Positional",
        "rules": [{"stages": ["C₁C₂", "C₂"]}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_rule_change_validates_identity_fixture():
    section = {
        "index": "10.2.2",
        "section": "Identity",
        "rules": [{"stages": ["V₀V₀", "V₀"]}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_rule_change_validates_identity_env_fixture():
    section = {
        "index": "10.2.4.2",
        "section": "Identity env",
        "rules": [{"stages": ["h", "ʔ"], "env": "V₀V₀"}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_rule_change_validates_matrix_attached_identity_fixture():
    section = {
        "index": "10.2.5",
        "section": "Matrix identity",
        "rules": [{"stages": ["V₀[+nas]V₀[-nas]", "V₀[+nas]"]}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_rule_change_validates_inter_slot_pharyngeal_fixture():
    section = {
        "index": "10.2.6",
        "section": "Inter-slot pharyngeal",
        "rules": [{"stages": ["C₁ˤC₂", "C₁C₂ˤ"]}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_rule_change_validates_optional_positional_fixture():
    section = {
        "index": "10.2.7",
        "section": "Optional positional",
        "rules": [{"stages": ["C₁C₂C₃C₄", "(C₃)C₄"]}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_rule_change_validates_identity_compound_length_fixture():
    section = {
        "index": "10.2.8",
        "section": "Identity compound length",
        "rules": [{"stages": ["C₀VC₀", "C₀ː"]}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(DiachronicSeries(section, "asca"), probe_words=probe)


def test_expand_subscript_references_optional_positional_compile_pipeline():
    assert compile_asca_rule_fields("C₁C₂C₃C₄", "(C₃)C₄") == "C=1 C=2 C=3 C=4 > {3}4"
