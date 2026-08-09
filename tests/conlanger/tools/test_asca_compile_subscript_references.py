"""Tests for compile-time positional/identity subscript expansion (ticket 40)."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from conlanger.tools.asca_compile.pipeline import compile_asca_rule_string
from conlanger.tools.asca_compile.subscript_references import (
    expand_index_subscript_references,
    is_easy_subscript_rule_text,
)
from conlanger.tools.asca_validator import validate_asca
from conlanger.tools.rules import SoundChangeRuleSet


@pytest.mark.parametrize(
    ("index_rule", "expected"),
    [
        ("C₁C₂ > C₂", "C=1 C=2 > 2"),
        ("V₀V₀ > V₀", "V=0 0 > 0"),
        ("h > ʔ / V₀V₀", "h > ʔ / _ V=0 0"),
    ],
)
def test_expand_index_subscript_references_happy_path(index_rule, expected):
    assert expand_index_subscript_references(index_rule) == expected


def test_expand_index_subscript_references_leaves_bracket_matrices_untouched():
    assert expand_index_subscript_references("C > V / [+high]") == "C > V / [+high]"
    assert expand_index_subscript_references("C₁[+high] > C₂") == "C=1[+high] > C=2"


def test_expand_index_subscript_references_prefixes_env_without_underscore():
    assert expand_index_subscript_references("h > ʔ / V₀") == "h > ʔ / _ V=0"


def test_expand_index_subscript_references_with_exception_block():
    assert (
        expand_index_subscript_references("C₁ > C₂ // except _#")
        == "C=1 > C=2 // except _#"
    )


def test_expand_index_subscript_references_reuses_declared_slot():
    assert expand_index_subscript_references("C₁C₁ > C₁") == "C=1 1 > 1"


def test_expand_index_subscript_references_without_arrow_expands_input_only():
    assert expand_index_subscript_references("C₁C₂") == "C=1 C=2 > "


@pytest.mark.parametrize(
    "text",
    [
        "C₀[+high]",
        "CˤC₂",
        "x₁₂",
    ],
)
def test_is_easy_subscript_rule_text_rejects_out_of_scope(text):
    assert is_easy_subscript_rule_text(text) is False


def test_is_easy_subscript_rule_text_accepts_in_scope():
    assert is_easy_subscript_rule_text("C₁ > C₂") is True


def test_compile_pipeline_applies_subscript_expansion_before_group_mappings():
    text = "C₁C₂ > C₂"
    assert compile_asca_rule_string(text) == expand_index_subscript_references(text)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_rule_change_validates_positional_slot_fixture():
    section = {
        "index": "10.2.1",
        "section": "Positional",
        "rules": [{"stages": ["C₁C₂", "C₂"]}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(SoundChangeRuleSet(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_rule_change_validates_identity_fixture():
    section = {
        "index": "10.2.2",
        "section": "Identity",
        "rules": [{"stages": ["V₀V₀", "V₀"]}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(SoundChangeRuleSet(section, "asca"), probe_words=probe)


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_rule_change_validates_identity_env_fixture():
    section = {
        "index": "10.2.4.2",
        "section": "Identity env",
        "rules": [{"stages": ["h", "ʔ"], "env": "V₀V₀"}],
    }
    probe = Path("tests/fixtures/asca_probe_words.wsca")
    validate_asca(SoundChangeRuleSet(section, "asca"), probe_words=probe)
