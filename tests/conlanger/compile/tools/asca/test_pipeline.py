"""Tests for the documented ASCA per-rule compile pipeline (ticket 39)."""

import pytest

from conlanger.compile.tools.asca.pipeline import (
    compile_asca_rule_fields,
)
from conlanger.ingest.models.mappings import CompilerConfig


@pytest.mark.parametrize(
    ("compiler_config", "rule_fields", "expected"),
    [
        pytest.param(
            CompilerConfig(series_mappings_global={"h₂": "ʔ"}),
            ("eh₂", "a", None, None),
            "eʔ > a",
            id="custom_global_mapping",
        ),
        pytest.param(CompilerConfig(), ("s₁", "ʃ", None, None), "s₁ > ʃ"),
        pytest.param(
            CompilerConfig(series_mappings_global={"h₁": "h"}),
            ("s₁", "ʃ", "_h₁", None),
            "s₁ > ʃ / _h",
            id="mapped_in_environment",
        ),
        pytest.param(
            CompilerConfig(series_mappings_global={"h₁": "h"}),
            ("a", "e", None, "_h₁"),
            "a > e // _h",
            id="mapped_in_exception",
        ),
    ],
)
def test_compile_applies_compiler_config_series_mappings(
    compiler_config, rule_fields, expected
):
    compiled = compile_asca_rule_fields(
        *rule_fields,
        compiler_config=compiler_config,
    )
    assert compiled == expected
