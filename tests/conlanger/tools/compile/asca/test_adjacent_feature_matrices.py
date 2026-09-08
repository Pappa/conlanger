"""Compile-time merge of adjacent ASCA feature matrices (ticket 124)."""

import shutil
from pathlib import Path

import pytest

from conlanger.appliers.asca import validate_asca
from conlanger.tools.compile.asca.pipeline import compile_asca_rule_fields
from conlanger.tools.compile.asca.tone_matrices import (
    merge_adjacent_feature_matrices,
    normalize_asca_adjacent_feature_matrices,
)
from conlanger.tools.rules import DiachronicSeries


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


def test_compile_sebirwa_s_chain_step_merges_adjacent_matrices(
    fx_sample_compiler_config,
):
    assert compile_asca_rule_fields(
        "S", "Sʰ", compiler_config=fx_sample_compiler_config
    ) == ("P > C:[+labial, +spread]")


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_sebirwa_s_chain_step_validates(fx_sample_compiler_config):
    section = {
        "index": "30.1.1.1",
        "section": "Proto-Bantu to Sebirwa",
        "rules": [{"stages": ["S", "Sʰ", "Aʰ"]}],
    }
    validate_asca(
        DiachronicSeries(section, "asca", compiler_config=fx_sample_compiler_config)
    )


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_adjacent_matrix_apply_probe(tmp_path: Path, fx_sample_compiler_config):
    """ASCA rejects C:[+labial][+spread]; merged colon form applies."""
    probe = tmp_path / "probe.wsca"
    probe.write_text("p.\n", encoding="utf-8")
    section = {
        "index": "124",
        "section": "adjacent-matrix-merge",
        "rules": [{"stages": ["P", "C:[+labial,+spread]"]}],
    }
    validate_asca(
        DiachronicSeries(section, "asca", compiler_config=fx_sample_compiler_config),
        probe_words=probe,
    )
