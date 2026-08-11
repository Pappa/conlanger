"""Tests for the documented ASCA per-rule compile pipeline (ticket 39)."""

from conlanger.tools.compile.asca.aliases import apply_asca_aliases
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
from conlanger.tools.compile.asca.superscript_modifiers import (
    normalize_asca_superscript_modifiers,
)
from conlanger.tools.rules import RuleChange


def test_asca_compile_pipeline_step_names_match_docs():
    assert ASCA_COMPILE_STEP_NAMES == (
        "normalize_asca_optional_grouping_ellipsis",
        "expand_index_subscript_references",
        "apply_section_local_abbreviations",
        "normalize_asca_superscript_modifiers",
        "apply_asca_group_mappings",
        "normalize_asca_length_marks",
        "normalize_typographic_apostrophes",
        "normalize_asca_ejective_marks",
        "apply_asca_aliases",
        "expand_meta_notation",
    )


def test_compile_asca_rule_string_matches_legacy_manual_chain():
    text = "tʃ:[+long]ʼ > tʃ:[+long]"
    mappings = {"S": "P"}
    manual = normalize_asca_optional_grouping_ellipsis(text)
    manual = normalize_asca_superscript_modifiers(manual, mappings)
    manual = apply_asca_group_mappings_to_string(manual, mappings)
    manual = normalize_asca_length_marks(manual)
    manual = normalize_typographic_apostrophes(manual)
    manual = normalize_asca_ejective_marks(manual)
    manual = apply_asca_aliases(manual)
    assert compile_asca_rule_string(text, group_mappings=mappings) == manual


def test_rule_change_uses_pipeline_for_asca():
    part = RuleChange({"input": "Vː", "output": "V", "env": "#C_C"}, "asca")
    expected = compile_asca_rule_string("Vː > V / #C_C", group_mappings={})
    assert part.value == expected
