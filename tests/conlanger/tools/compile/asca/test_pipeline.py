"""Tests for the documented ASCA per-rule compile pipeline (ticket 39)."""

import pytest

from conlanger.tools.compile.asca.pipeline import (
    compile_asca_rule_field_strings,
    compile_asca_rule_fields,
)
from conlanger.tools.compile.asca.structures import join_asca_rule_fields
from conlanger.utils.mappings import CompilerConfig


@pytest.mark.parametrize(
    ("compiler_config", "inp", "output", "env", "exception", "expected"),
    [
        (
            CompilerConfig(series_mappings_global={"h₂": "ʔ"}),
            "eh₂",
            "a",
            None,
            None,
            "eʔ > a",
        ),
        (CompilerConfig(), "s₁", "ʃ", None, None, "s₁ > ʃ"),
        (
            CompilerConfig(series_mappings_global={"h₁": "h"}),
            "s₁",
            "ʃ",
            "_h₁",
            None,
            "s₁ > ʃ / _h",
        ),
        (
            CompilerConfig(series_mappings_global={"h₁": "h"}),
            "a",
            "e",
            None,
            "_h₁",
            "a > e // _h",
        ),
        (
            CompilerConfig(series_mappings_global={"h₂": "x"}),
            "eh₂",
            "a",
            None,
            None,
            "ex > a",
        ),
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
    compiler_config, inp, output, env, exception, expected
):
    compiled = compile_asca_rule_fields(
        inp,
        output,
        env,
        exception,
        compiler_config=compiler_config,
    )
    assert compiled == expected


def test_compile_asca_rule_field_strings_matches_joined_compile():
    inp, output, env, exception = "eh₂", "a", None, None
    field_strings = compile_asca_rule_field_strings(
        inp,
        output,
        env,
        exception,
        compiler_config=CompilerConfig(series_mappings_global={"h₂": "ʔ"}),
    )
    assert join_asca_rule_fields(*field_strings) == compile_asca_rule_fields(
        inp,
        output,
        env,
        exception,
        compiler_config=CompilerConfig(series_mappings_global={"h₂": "ʔ"}),
    )
