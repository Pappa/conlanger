"""Tests for the documented ASCA per-rule compile pipeline (ticket 39)."""

from conlanger.tools.compile.asca.apostrophes import normalize_typographic_apostrophes
from conlanger.tools.compile.asca.ejectives import normalize_asca_ejective_marks
from conlanger.tools.compile.asca.ellipsis import (
    normalize_asca_optional_grouping_ellipsis,
)
from conlanger.tools.compile.asca.group_mappings import (
    apply_asca_group_mappings_to_string,
)
from conlanger.tools.compile.asca.length_marks import normalize_asca_length_marks
from conlanger.tools.compile.asca.pipeline import (
    ASCA_COMPILE_STEP_NAMES,
    compile_asca_rule_string,
)
from conlanger.tools.compile.asca.series_mappings import apply_compiler_series_mappings
from conlanger.tools.compile.asca.superscript_modifiers import (
    normalize_asca_superscript_modifiers,
)
from conlanger.tools.compile.asca.tone_matrices import normalize_asca_tone_matrices
from conlanger.tools.rules import DiachronicSeries, SoundChangeRule
from conlanger.utils.file_io import load_compiler_config
from conlanger.utils.mappings import CompilerConfig


def test_asca_compile_pipeline_step_names_match_docs():
    assert ASCA_COMPILE_STEP_NAMES == (
        "normalize_asca_optional_grouping_ellipsis",
        "apply_compiler_series_mappings",
        "expand_index_subscript_references",
        "apply_section_local_abbreviations",
        "normalize_asca_superscript_modifiers",
        "apply_asca_group_mappings",
        "normalize_asca_length_marks",
        "normalize_asca_tone_matrices",
        "normalize_typographic_apostrophes",
        "normalize_asca_ejective_marks",
        "expand_meta_notation",
    )


def test_compile_asca_rule_string_matches_legacy_manual_chain():
    text = "tʃ:[+long]ʼ > tʃ:[+long]"
    mappings = {"S": "P"}
    config = load_compiler_config()
    manual = normalize_asca_optional_grouping_ellipsis(text)
    manual = apply_compiler_series_mappings(
        manual, section_index="", compiler_config=config
    )
    manual = normalize_asca_superscript_modifiers(manual, mappings)
    manual = apply_asca_group_mappings_to_string(manual, mappings)
    manual = normalize_asca_length_marks(manual)
    manual = normalize_asca_tone_matrices(manual)
    manual = normalize_typographic_apostrophes(manual)
    manual = normalize_asca_ejective_marks(manual)
    assert compile_asca_rule_string(text, group_mappings=mappings) == manual


def test_rule_change_uses_pipeline_for_asca():
    part = SoundChangeRule({"input": "Vː", "output": "V", "env": "#C_C"})
    expected = compile_asca_rule_string("Vː > V / #C_C", group_mappings={})
    assert part.value == expected


def test_compile_applies_compiler_config_series_mappings():
    config = CompilerConfig(series_mappings_global={"h₂": "ʔ"})
    compiled = compile_asca_rule_string(
        "eh₂ > a",
        group_mappings={},
        compiler_config=config,
    )
    assert compiled == "eʔ > a"


def test_compile_leaves_unmapped_series_indices_literal():
    config = CompilerConfig()
    compiled = compile_asca_rule_string(
        "s₁ > ʃ",
        group_mappings={},
        compiler_config=config,
    )
    assert compiled == "s₁ > ʃ"


def test_compile_applies_mapped_indices_in_environment():
    config = CompilerConfig(series_mappings_global={"h₁": "h"})
    compiled = compile_asca_rule_string(
        "s₁ > ʃ / _h₁",
        group_mappings={},
        compiler_config=config,
    )
    assert compiled == "s₁ > ʃ / _h"


def test_compile_applies_mapped_indices_in_exception():
    config = CompilerConfig(series_mappings_global={"h₁": "h"})
    compiled = compile_asca_rule_string(
        "a > e // _h₁",
        group_mappings={},
        compiler_config=config,
    )
    assert compiled == "a > e // _h"


def test_compile_default_config_maps_pie_laryngeals():
    compiled = compile_asca_rule_string("eh₂ > a", group_mappings={})
    assert compiled == "ex > a"


def test_diachronic_series_applies_section_series_mappings():
    config = CompilerConfig(
        series_mappings_global={"h₁": "h"},
        series_mappings_sections={"17.10": {"h₁": "ʔ"}},
    )
    section = {
        "index": "17.10",
        "section": "test",
        "rules": [{"stages": ["h₁", "a"], "raw": "h₁ → a", "source": "t:1"}],
    }
    rendered = str(DiachronicSeries(section, compiler_config=config))
    assert "ʔ > a" in rendered
