"""Tests for parallel output set ∅ expansion (ticket 81)."""

import shutil

import pytest

from conlanger.tools.compile.asca.parallel_output_null import (
    expand_parallel_output_null_branches,
)
from conlanger.tools.rules import DiachronicSeries, SoundChangeRule


@pytest.mark.parametrize(
    ("input_text", "output_text", "expected_branches"),
    [
        ("{r,h}", "{∅,h}", [("r", "∅"), ("h", "h")]),
        ("{pʰ,ŋ}", "{∅,j}", [("pʰ", "∅"), ("ŋ", "j")]),
        ("{m,ɲ} n", "{ɲ,∅} {ŋ,∅}", [("m n", "ɲ ŋ"), ("ɲ n", "∅")]),
        ("m l", "{m,n} {l,∅}", [("m l", "m l"), ("m l", "n")]),
        ("p k", "ɸ {∅,k}", [("p k", "ɸ"), ("p k", "ɸ k")]),
        ("{tʰ,d} {k,ɡ}", "r {h,∅}", [("tʰ k", "r h"), ("d ɡ", "r")]),
        ("{b,k} r", "{r,∅}", [("b r", "r"), ("k r", "∅")]),
    ],
)
def test_expand_parallel_output_null_branches(
    input_text, output_text, expected_branches
):
    assert (
        expand_parallel_output_null_branches(input_text, output_text)
        == expected_branches
    )


@pytest.mark.parametrize(
    ("input_text", "output_text"),
    [
        ("k b r", "{ŋ,∅} {w,m} {n,r,t}"),  # uneven branch counts across columns
        ("d", "{∅,ð}"),  # optional-output shape — expander returns None
        ("c ɲ", "∅ n"),  # top-level column null — ticket 60
    ],
)
def test_expand_parallel_output_null_branches_out_of_scope(input_text, output_text):
    assert expand_parallel_output_null_branches(input_text, output_text) is None


def test_paired_null_set_builds_alternatives():
    rule = SoundChangeRule({"input": "{r,h}", "output": "{∅,h}"})
    assert len(rule.alternatives) == 2
    assert [alt.value for alt in rule.alternatives] == ["r > ∅", "h > h"]


def test_multi_column_null_set_alternatives():
    rule = SoundChangeRule({"input": "{m,ɲ} n", "output": "{ɲ,∅} {ŋ,∅}", "env": "_#"})
    assert len(rule.alternatives) == 2
    assert rule.alternatives[0].value == "m n > ɲ ŋ / _#"
    assert rule.alternatives[1].value == "ɲ n > ∅ / _#"


def test_optional_output_still_wins_over_parallel_null_expander():
    rule = SoundChangeRule({"input": "d", "output": "{∅,ð}", "env": "V_V"})
    assert len(rule.alternatives) == 2
    assert [alt.output for alt in rule.alternatives] == ["∅", "ð"]


def test_parallel_null_alternatives_are_leaf_peers():
    rule = SoundChangeRule({"input": "{r,h}", "output": "{∅,h}"})
    for alt in rule.alternatives:
        assert alt.alternatives == []


def test_peel_trailing_env_from_merged_output_stage():
    rule = SoundChangeRule(
        {"input": "ŋ", "output": "{∅,n} #_ else"},
    )
    assert len(rule.alternatives) == 2
    assert rule.alternatives[0].value == "ŋ > ∅ / #_ else"
    assert rule.alternatives[1].value == "ŋ > n / #_ else"


@pytest.mark.skipif(shutil.which("asca") is None, reason="asca binary not on PATH")
def test_parallel_null_alternatives_validate_independently():
    from pathlib import Path

    from conlanger.appliers.asca import validate_asca

    probe = Path("tests/fixtures/asca_probe_words.wsca")
    rule = SoundChangeRule({"input": "{r,h}", "output": "{∅,h}"})
    for alt in rule.alternatives:
        section = {
            "index": "10.1.1.1",
            "section": "Balinese",
            "rules": [{"stages": [alt.input, alt.output]}],
        }
        validate_asca(DiachronicSeries(section), probe_words=probe)
