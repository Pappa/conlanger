"""Tests for compile-time positional/identity subscript expansion (ticket 40)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.compile.asca.structures import (
    ENV_SEPARATOR,
    EXCEPTION_SEPARATOR,
    OUTPUT_SEPARATOR,
    join_asca_rule_fields,
)
from conlanger.tools.compile.asca.subscript_references import (
    expand_subscript_references_across_fields,
)
from conlanger.tools.rules import DiachronicSeries


def _split_joined_rule(text: str) -> tuple[str, str, str | None, str | None]:
    exception: str | None = None
    if EXCEPTION_SEPARATOR in text:
        text, exception = text.split(EXCEPTION_SEPARATOR, 1)
    env: str | None = None
    if OUTPUT_SEPARATOR in text:
        inp, rest = text.split(OUTPUT_SEPARATOR, 1)
        if ENV_SEPARATOR in rest:
            output, env = rest.split(ENV_SEPARATOR, 1)
        else:
            output = rest
    else:
        inp = text
        output = ""
    return inp, output, env, exception


def _expand_joined_subscripts(text: str) -> str:
    if not text:
        return text
    inp, output, env, exception = _split_joined_rule(text)
    inp, output, env, exception = expand_subscript_references_across_fields(
        inp, output, env, exception
    )
    return join_asca_rule_fields(inp, output, env, exception)


@pytest.mark.parametrize(
    ("index_rule", "expected"),
    [
        ("C₁C₂ > C₂", "C=1 C=2 > 2"),
        ("V₀V₀ > V₀", "V=0 0 > 0"),
        ("h > ʔ / V₀V₀", "h > ʔ / _ V=0 0"),
    ],
)
def test_expand_subscript_references_happy_path(index_rule, expected):
    assert _expand_joined_subscripts(index_rule) == expected


def test_expand_subscript_references_leaves_bare_feature_matrices_untouched():
    assert _expand_joined_subscripts("C > V / [+high]") == "C > V / [+high]"


def test_expand_subscript_references_matrix_attached_identity():
    assert (
        _expand_joined_subscripts("V₀[+nas]V₀[-nas] > V₀[+nas]")
        == "V:[+nas]=0 V:[-nas]=0 > 0:[+nas]"
    )


def test_expand_subscript_references_matrix_attached_positional():
    assert _expand_joined_subscripts("C₁[+high] > C₂") == "C:[+high]=1 > C=2"
    assert (
        _expand_joined_subscripts("CV₁CV:[+stress]₂ > CV₂CV:[+stress]₂")
        == "CV=1 CV:[+stress]=2 > 2 2:[+stress]"
    )


def test_expand_subscript_references_prefixes_env_without_underscore():
    assert _expand_joined_subscripts("h > ʔ / V₀") == "h > ʔ / _ V=0"


def test_expand_subscript_references_with_exception_block():
    assert _expand_joined_subscripts("C₁ > C₂ // except _#") == "C=1 > C=2 // except _#"


def test_expand_subscript_references_reuses_declared_slot():
    assert _expand_joined_subscripts("C₁C₁ > C₁") == "C=1 1 > 1"


def test_expand_subscript_references_without_arrow_expands_input_only():
    assert _expand_joined_subscripts("C₁C₂") == "C=1 C=2 > "


def test_compile_pipeline_applies_subscript_expansion_before_group_mappings():
    inp, output = "C₁C₂", "C₂"
    assert compile_asca_rule_fields(inp, output, group_mappings={}) == (
        _expand_joined_subscripts(f"{inp} > {output}")
    )


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


def test_expand_subscript_references_inter_slot_pharyngeal():
    assert (
        _expand_joined_subscripts("C₁ˤC₂ > C₁C₂ˤ")
        == "C:[+pharyn]=1 C=2 > 1 2:[+pharyn]"
    )


def test_expand_subscript_references_identity_compounds():
    assert _expand_joined_subscripts("mn > mV₀nV₀ / #_") == "mn > mV=0 n0 / #_"
    assert _expand_joined_subscripts("CʔV₀ > CV₀ʔV₀") == "CʔV=0 > C0 ʔ0"
    assert _expand_joined_subscripts("C₀VC₀ > C₀ː") == "C=0 V0 > 0ː"


def test_expand_subscript_references_optional_positional():
    assert _expand_joined_subscripts("C₁C₂C₃C₄ > (C₃)C₄") == "C=1 C=2 C=3 C=4 > {3}4"
    assert (
        compile_asca_rule_fields("C₁C₂C₃C₄", "(C₃)C₄", group_mappings={})
        == "C=1 C=2 C=3 C=4 > {3}4"
    )


def test_expand_subscript_references_leaves_prose_env_and_exception():
    assert (
        _expand_joined_subscripts("C₁C₂ > xC₂ / if C₂ was a plosive or s")
        == "C=1 C=2 > x2 / if C₂ was a plosive or s"
    )
    assert (
        _expand_joined_subscripts("ɣ > ʔ / VV₀_V₀ // V₀ = U")
        == "ɣ > ʔ / VV=0 _0 // V₀ = U"
    )


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
