"""Compile-time merge of adjacent ASCA feature matrices (tickets 124, 133)."""

import pytest

from conlanger.compile.tools.asca.pipeline import (
    compile_asca_rule_field_strings,
    compile_asca_rule_fields,
)
from conlanger.compile.tools.asca.tone_matrices import (
    merge_adjacent_feature_matrices,
    normalize_asca_adjacent_feature_matrices,
)
from conlanger.scripts.config_loaders import load_compiler_config


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("C:[+labial][+spread]", "C:[+labial, +spread]"),
        ("P > C:[+labial][+spread]", "P > C:[+labial, +spread]"),
        ("V:[+long] C:[+spread]", "V:[+long] C:[+spread]"),
        ("V:[+long][+spread]", "V:[+long, +spread]"),
        ("V:[+long][tone: 51]", "V:[+long, tone: 51]"),
        ("b:[+spread,+voice][+long]", "b:[+spread,+voice, +long]"),
        ("[+labial][+spread]", "[+labial, +spread]"),
        ("V:[+front]:[+stress]", "V:[+front, +stress]"),
        ("_V:[+front]:[+stress]", "_V:[+front, +stress]"),
        ("V_V:[+front]:[+stress]", "V_V:[+front, +stress]"),
        ("V:[+back]:[+stress]", "V:[+back, +stress]"),
        ("V:[+long]:[+spread]:[+stress]", "V:[+long, +spread, +stress]"),
        ("", ""),
        ("plain", "plain"),
    ],
)
def test_merge_adjacent_feature_matrices(text, expected):
    assert merge_adjacent_feature_matrices(text) == expected


def test_normalize_asca_adjacent_feature_matrices_alias():
    assert (
        normalize_asca_adjacent_feature_matrices("C:[+labial][+spread]")
        == "C:[+labial, +spread]"
    )
    assert (
        normalize_asca_adjacent_feature_matrices("V:[+front]:[+stress]")
        == "V:[+front, +stress]"
    )


@pytest.mark.parametrize(
    ("inp", "output", "env", "expected_env"),
    [
        ("kʷ", "s", "_E:[+stress]", "_V:[+front, +stress]"),
        ("j", "∅", "V_E:[+stress]", "V_V:[+front, +stress]"),
        ("t", "tʃ", "_V:[+front]:[+stress]", "_V:[+front, +stress]"),
        ("dj", "ʒ", "_V:[+back]:[+stress]", "_V:[+back, +stress]"),
    ],
)
def test_compile_env_colon_chained_stress_matrices(inp, output, env, expected_env):
    cfg = load_compiler_config()
    compiled = compile_asca_rule_field_strings(
        inp, output, env=env, compiler_config=cfg
    )
    assert compiled[2] == expected_env


def test_compile_sebirwa_s_chain_step_merges_adjacent_matrices(
    fx_sample_compiler_config,
):
    assert compile_asca_rule_fields(
        "S", "Sʰ", compiler_config=fx_sample_compiler_config
    ) == ("P > C:[+labial, +spread]")
