"""Tests for the documented ASCA per-rule compile pipeline (ticket 39)."""

import pytest

from conlanger.tools.compile.asca.pipeline import (
    compile_asca_rule_string,
)
from conlanger.utils.mappings import CompilerConfig


@pytest.mark.parametrize(
    ("compiler_config", "text", "expected"),
    [
        (CompilerConfig(series_mappings_global={"h₂": "ʔ"}), "eh₂ > a", "eʔ > a"),
        (CompilerConfig(), "s₁ > ʃ", "s₁ > ʃ"),
        (
            CompilerConfig(series_mappings_global={"h₁": "h"}),
            "s₁ > ʃ / _h₁",
            "s₁ > ʃ / _h",
        ),
        (
            CompilerConfig(series_mappings_global={"h₁": "h"}),
            "a > e // _h₁",
            "a > e // _h",
        ),
        (None, "eh₂ > a", "ex > a"),
    ],
    ids=[
        "custom_global_mapping",
        "unmapped_left_literal",
        "mapped_in_environment",
        "mapped_in_exception",
        "default_pie_laryngeals",
    ],
)
def test_compile_applies_compiler_config_series_mappings(
    compiler_config, text, expected
):
    compiled = compile_asca_rule_string(
        text,
        group_mappings={},
        compiler_config=compiler_config,
    )
    assert compiled == expected
